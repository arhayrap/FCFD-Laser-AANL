# ============================================================
#  watchdog_treev11.py
#  One canvas, 3 rows x len(CHANNELS) pads:
#    Row 1: amp[ch]
#    Row 2: LP2_50[ch]
#    Row 3: LP2_50[ch] - LP2_50[REF_CH]  with Gaussian fit
#
#  Drawing strategy:
#    When file N arrives  → draw file N-1
#    File 1 is held until file 2 arrives, and so on.
#    The last file is never drawn.
# ============================================================

import ROOT
import time
import os
import queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

"""
0 - trigger
1 - analog 1 strip
2 - digital 1 strip
3 - analog 2 strip
4 - digital 2 strip
5 - analog 3 strip
6 - digital 3 strip
7 - none
"""

# WATCH_DIR = "/home/cmspractice/FCFD-Project/ToWatch"
# WATCH_DIR = "/home/cmspractice/FCFD-Project/FCFD-Laser-main/DAQ/PreProcessed"
WATCH_DIR = "/home/cmspractice/FCFD-Project/Data/PreProcessed"

TREE_NAME = "pulse"
REF_CH    = 0   # reference channel for LP2_50 difference (trigger channel)

# Each row: [ channel_index, amp_title, amp_xlabel, amp_ylabel, amp_cut,
#             lp250_title, lp250_xlabel, lp250_ylabel, lp250_cut,
#             diff_title, diff_xlabel, diff_ylabel ]
#
# Cut syntax examples:
#   ""                              → no cut
#   "amp[2] > 10"                   → single threshold
#   "amp[2] > 10 && amp[2] < 500"  → range cut
CHANNELS = [
    # [ 0, "Laser Trigger [i0]",  "Amplitude [mV]", "Counts", "", "LP2_50 LT", "[ns]", "Counts", "", "LP2_50 LT - ch0", "[ns]", "Counts" ],
    # [ 1, "Analog 1 [i1]",       "Amplitude [mV]", "Counts", "", "LP2_50 A1", "[ns]", "Counts", "", "LP2_50 A1 - ch0", "[ns]", "Counts" ],
    [ 2, "Digital 1 [i2]",      "Amplitude [mV]", "Counts", "", "LP2_50 D1", "[ns]", "Counts", "", "dT for D1", "[ns]", "Counts" ],
    # [ 3, "Analog 2 [i3]",       "Amplitude [mV]", "Counts", "", "LP2_50 A2", "[ns]", "Counts", "", "LP2_50 A2 - ch0", "[ns]", "Counts" ],
    [ 4, "Digital 2 [i4]",      "Amplitude [mV]", "Counts", "", "LP2_50 D2", "[ns]", "Counts", "", "dT for D2", "[ns]", "Counts" ],
    # [ 5, "Analog 3 [i5]",       "Amplitude [mV]", "Counts", "", "LP2_50 A3", "[ns]", "Counts", "", "LP2_50 A3 - ch0", "[ns]", "Counts" ],
    [ 6, "Digital 3 [i6]",      "Amplitude [mV]", "Counts", "", "LP2_50 D3", "[ns]", "Counts", "", "dT for D3", "[ns]", "Counts" ],
]

COLORS = [
    ROOT.kBlue+1, ROOT.kRed+1,      ROOT.kGreen+2,
    ROOT.kOrange+1, ROOT.kViolet+1, ROOT.kCyan+2, ROOT.kMagenta+1
]

ROOT.gStyle.SetOptStat("emr")
ROOT.gStyle.SetOptFit(1)       # show fit parameters: chi2, prob, p0, p1...
ROOT.gStyle.SetStatFontSize(0.15)
ROOT.gStyle.SetTitleFontSize(0.09)
ROOT.gStyle.SetLabelSize(0.04, "XY")
ROOT.gStyle.SetTitleSize(0.04, "XY")
ROOT.gROOT.SetBatch(False)

# ── Create one canvas with 3 rows x len(CHANNELS) pads ────────
n = len(CHANNELS)
c = ROOT.TCanvas("c", "Live Pulse Monitor", 300 * n, 1200)

pads_amp  = []
pads_lp   = []
pads_diff = []

for i, row in enumerate(CHANNELS):
    ch = row[0]
    x_low  =  i      / n
    x_high = (i + 1) / n

    c.cd()
    p_amp = ROOT.TPad(f"pad_amp_{ch}", f"pad_amp_{ch}",
                      x_low, 2/3, x_high, 1.0)
    p_amp.SetGrid()
    p_amp.SetLeftMargin(0.2)
    p_amp.SetBottomMargin(0.2)
    p_amp.SetTopMargin(0.2)
    p_amp.Draw()
    pads_amp.append(p_amp)

    c.cd()
    p_lp = ROOT.TPad(f"pad_lp_{ch}", f"pad_lp_{ch}",
                     x_low, 1/3, x_high, 2/3)
    p_lp.SetGrid()
    p_lp.SetLeftMargin(0.2)
    p_lp.SetBottomMargin(0.2)
    p_lp.SetTopMargin(0.2)
    p_lp.Draw()
    pads_lp.append(p_lp)

    c.cd()
    p_diff = ROOT.TPad(f"pad_diff_{ch}", f"pad_diff_{ch}",
                       x_low, 0.0, x_high, 1/3)
    p_diff.SetGrid()
    p_diff.SetLeftMargin(0.2)
    p_diff.SetBottomMargin(0.2)
    p_diff.SetTopMargin(0.2)
    p_diff.Draw()
    pads_diff.append(p_diff)

c.Update()

# ── Keeps histograms alive between draws so resize doesn't crash
live_hists = []

# ── Holds the previous file path — drawn when the next file arrives
previous_filepath = None

# ── Helper: style and draw a histogram on a pad ───────────────
def draw_hist(pad, h, color, title, xlabel, ylabel):
    # Set title and axis labels AFTER filling — overrides ROOT's defaults
    h.SetTitle(title)
    h.GetXaxis().SetTitle(xlabel)
    h.GetYaxis().SetTitle(ylabel)
    h.SetDirectory(0)   # detach from file — survives fIn.Close()
    h.SetLineColor(color)
    h.SetLineWidth(2)
    h.GetXaxis().SetLabelSize(0.07)
    h.GetYaxis().SetLabelSize(0.07)
    h.GetXaxis().SetTitleSize(0.07)
    h.GetYaxis().SetTitleSize(0.07)
    pad.cd()
    pad.Clear()
    h.Draw("HIST")
    pad.Update()

# ── Helper: Gaussian fit on a diff histogram ──────────────────
def fit_gaussian(pad, h, color):
    if h.GetEntries() < 10:
        print(f"  [WARN] Not enough entries to fit {h.GetName()}, skipping.")
        return None

    # Initial parameter estimates from histogram stats
    mean  = h.GetMean()
    sigma = h.GetStdDev()

    # Fit range: mean ± 2 sigma
    fit_low  = mean - 2.0 * sigma
    fit_high = mean + 2.0 * sigma

    gaus = ROOT.TF1(f"gaus_{h.GetName()}", "gaus", fit_low, fit_high)
    gaus.SetLineColor(ROOT.kRed)
    gaus.SetLineWidth(2)

    # "R"  → fit within the TF1 range
    # "Q"  → quiet mode (no printout to terminal)
    # "S"  → store fit result
    fit_result = h.Fit(gaus, "RQS")

    pad.cd()
    h.Draw("HIST")       # redraw histogram on top of fit
    gaus.Draw("SAME")    # overlay fit curve

    # Print results to terminal
    print(f"    Fit {h.GetName()}: "
          f"mean = {gaus.GetParameter(1):.3f} ns, "
          f"sigma = {gaus.GetParameter(2):.3f} ns, "
          f"chi2/ndf = {gaus.GetChisquare():.2f}/{gaus.GetNDF()}")

    pad.Update()
    return gaus

# ── Draw function — called only from the main thread ──────────
def draw_file(filepath):
    global live_hists
    print(f"Drawing: {filepath}")

    fIn = ROOT.TFile.Open(filepath, "READ")
    if not fIn or fIn.IsZombie():
        print(f"  [ERROR] Cannot open {filepath}")
        return

    tree = fIn.Get(TREE_NAME)
    if not tree:
        print(f"  [ERROR] TTree '{TREE_NAME}' not found.")
        fIn.Close()
        return

    new_hists = []

    # ── Step 1: amp and LP2_50 via TTree::Draw (no SetBranchAddress yet)
    for i, row in enumerate(CHANNELS):
        ch                                              = row[0]
        amp_title,  amp_xlabel,  amp_ylabel,  amp_cut  = row[1], row[2], row[3], row[4]
        lp_title,   lp_xlabel,   lp_ylabel,   lp_cut   = row[5], row[6], row[7], row[8]

        # amp — let ROOT create the histogram in gDirectory, then retrieve it
        tree.Draw(f"amp[{ch}]>>h_amp_{ch}", amp_cut, "goff")
        h_amp = ROOT.gDirectory.Get(f"h_amp_{ch}")
        draw_hist(pads_amp[i], h_amp, COLORS[ch], amp_title, amp_xlabel, amp_ylabel)
        new_hists.append(h_amp)

        # LP2_50
        # tree.Draw(f"LP2_50[{ch}]>>h_lp_{ch}", lp_cut, "goff")
        # h_lp = 1e9 * ROOT.gDirectory.Get(f"h_lp_{ch}")
        tree.Draw(f"LP2_50[{ch}]*1e9>>h_lp_{ch}", lp_cut, "goff")
        h_lp = ROOT.gDirectory.Get(f"h_lp_{ch}")

        draw_hist(pads_lp[i], h_lp, COLORS[ch], lp_title, lp_xlabel, lp_ylabel)
        new_hists.append(h_lp)

    # ── Step 2: set branch address for diff event loop ────────
    # Done AFTER all tree.Draw calls to avoid interference
    lp2_50 = ROOT.std.vector('float')(7)
    tree.SetBranchAddress("LP2_50", lp2_50.data())

    for i, row in enumerate(CHANNELS):
        ch                                       = row[0]
        diff_title, diff_xlabel, diff_ylabel     = row[9], row[10], row[11]

        h_diff = ROOT.TH1F(f"h_diff_{ch}", "", 100, 0, 0)

        # # without cut
        # for ev in range(tree.GetEntries()):
        #     tree.GetEntry(ev)
        #     h_diff.Fill((lp2_50[ch] - lp2_50[REF_CH]) * 1e9)

        # # with cut
        for ev in range(tree.GetEntries()):
            tree.GetEntry(ev)
            diff_ns = (lp2_50[ch] - lp2_50[REF_CH]) * 1e9
            if diff_ns < 45:
                h_diff.Fill(diff_ns)

        draw_hist(pads_diff[i], h_diff, COLORS[ch], diff_title, diff_xlabel, diff_ylabel)

        # Gaussian fit drawn on top
        gaus = fit_gaussian(pads_diff[i], h_diff, COLORS[ch])

        new_hists.append(h_diff)
        if gaus:
            new_hists.append(gaus)   # keep fit function alive too

    # ── Step 3: reset branch addresses so next file is clean ──
    tree.ResetBranchAddresses()

    c.SetTitle(f"Live Monitor for: {os.path.basename(filepath)}")
    c.Update()

    # Replace persistent store — old histograms released here
    live_hists = new_hists

    nentries = tree.GetEntries()
    fIn.Close()
    print(f"  Done. {nentries} entries.")

# ── Watchdog: only puts filepath into queue, no ROOT calls ────
file_queue = queue.Queue()

class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith(".root"):
            return
        file_queue.put(event.src_path)

# ── Main loop (all ROOT calls happen here) ────────────────────
if __name__ == "__main__":
    print(f"Watching: {WATCH_DIR}")
    print(f"Displaying channels: {[row[0] for row in CHANNELS]}")
    print(f"Reference channel for diff: {REF_CH}")
    print("Waiting for new .root files... (Ctrl+C to stop)\n")

    handler  = NewFileHandler()
    observer = Observer()
    observer.schedule(handler, path=WATCH_DIR, recursive=False)
    observer.start()

    try:
        while True:
            ROOT.gSystem.ProcessEvents()

            try:
                new_filepath = file_queue.get_nowait()

                if previous_filepath is None:
                    # First file — just hold it, wait for the next one
                    print(f"  Received first file, waiting for next: {os.path.basename(new_filepath)}")
                else:
                    # A new file arrived — draw the previous (now fully written) one
                    print(f"  New file arrived ({os.path.basename(new_filepath)}), drawing previous: {os.path.basename(previous_filepath)}")
                    draw_file(previous_filepath)

                previous_filepath = new_filepath

            except queue.Empty:
                pass

            time.sleep(0.2)

    except KeyboardInterrupt:
        observer.stop()
        print("\nStopped.")

    observer.join()
