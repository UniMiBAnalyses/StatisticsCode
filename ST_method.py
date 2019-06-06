import ROOT
import sys
from math import *

if __name__ == '__main__':
    
    infile = sys.argv[1]       
    f = ROOT.TFile(infile, 'READ')
    
    n0 = f.Get('numerator0')
    n1 = f.Get('numerator1')
    n2 = f.Get('numerator2')
    n3 = f.Get('numerator3')
    n4 = f.Get('numerator4')
    n6 = f.Get('numerator6')
    n8 = f.Get('numerator8')
    d0 = f.Get('denominator0')
    d1 = f.Get('denominator1')
    d2 = f.Get('denominator2')
    d3 = f.Get('denominator3')
    d4 = f.Get('denominator4')
    d6 = f.Get('denominator6')
    d8 = f.Get('denominator8')
    
    x_cut = n0.GetX()
    tot0 = d0.GetY()
    tot1 = d1.GetY()
    tot2 = d2.GetY()
    tot3 = d3.GetY()
    tot4 = d4.GetY()
    tot6 = d6.GetY()
    tot8 = d8.GetY()
    pass0 = n0.GetY()
    pass1 = n1.GetY()
    pass2 = n2.GetY()
    pass3 = n3.GetY()
    pass4 = n4.GetY()
    pass6 = n6.GetY()
    pass8 = n8.GetY()
    
    g = ROOT.TGraphErrors()
    g.SetName('eff_ST')
    g_norm = ROOT.TGraphErrors()
    g_norm.SetName('eff_norm_ST')
    
    for i in range(0, len(x_cut)):
        notpass0 = tot0[i]-pass0[i]
        notpass1 = tot1[i]-pass1[i]
        notpass2 = tot2[i]-pass2[i]
        notpass3 = tot3[i]-pass3[i]
        notpass4 = tot4[i]-pass4[i]
        notpass6 = tot6[i]-pass6[i]
        notpass8 = tot8[i]-pass8[i]
        err_notpass = max(fabs(notpass1-notpass0), fabs(notpass2-notpass0), \
        fabs(notpass3-notpass0), fabs(notpass4-notpass0), fabs(notpass6-notpass0), fabs(notpass8-notpass0))
        err_tot = max(fabs(tot1[i]-tot0[i]), fabs(tot2[i]-tot0[i]), fabs(tot3[i]-tot0[i]), \
        fabs(tot4[i]-tot0[i]), fabs(tot6[i]-tot0[i]), fabs(tot8[i]-tot0[i]))
        err = sqrt( (err_notpass/tot0[i])**2 + ((notpass0*err_tot)/(tot0[i]**2))**2 ) # --> propagation of errors
        g.SetPoint(i, x_cut[i], 1 - notpass0/tot0[i])
        g.SetPointError(i, 0, err)
        g_norm.SetPoint(i, x_cut[i], 1)
        g_norm.SetPointError(i, 0, err/(1-notpass0/tot0[i]))

    if infile[:-9] == 'jv':
        g.SetFillColor(ROOT.kBlue+2)
        g.SetLineColor(ROOT.kBlue)
        g_norm.SetFillColor(ROOT.kBlue+2)
        g.GetXaxis().SetTitle('p_{t} jet 3 [GeV]')
        g_norm.GetXaxis().SetTitle('p_{t} jet 3 [GeV]')
    elif infile[:-9] == 'cjv':
        g.SetFillColor(ROOT.kRed+1)
        g_norm.SetLineColor(ROOT.kRed)
        g_norm.SetFillColor(ROOT.kRed+1)
        g.GetXaxis().SetTitle('p_{t} jet 3 [GeV]')
        g_norm.GetXaxis().SetTitle('p_{t} jet 3 [GeV]')
    elif infile[:-9] == 'djv':
        g.SetFillColor(ROOT.kGreen+2)
        g_norm.SetLineColor(ROOT.kGreen)
        g_norm.SetFillColor(ROOT.kGreen+2)
        g.GetXaxis().SetTitle('r')
        g_norm.GetXaxis().SetTitle('r')
    elif infile[:-9] == 'dcjv':
        g.SetFillColor(ROOT.kPink-9)
        g_norm.SetLineColor(ROOT.kPink-8)
        g_norm.SetFillColor(ROOT.kPink-9)
        g.GetXaxis().SetTitle('r')
        g_norm.GetXaxis().SetTitle('r')
    
    g.GetXaxis().SetTitleSize(0.04)
    g_norm.GetXaxis().SetTitleSize(0.04)
    g.GetYaxis().SetTitle('#varepsilon')
    g.GetYaxis().SetTitleSize(0.045)
    g.GetYaxis().SetTitleOffset(0.8)
    g_norm.SetFillStyle(3001)
    g_norm.SetLineWidth(2)
    g.SetFillStyle(3001)
    g.SetLineWidth(2)
        
    outfile = ROOT.TFile(infile[:-9]+'_ST.root', 'RECREATE')
    g.Write()
    g_norm.Write()
    
    canva = ROOT.TCanvas('canva', "", 100, 200, 700, 500)
    canva.cd()
    g.Draw('AP4C')
    canva.SaveAs('{}_ST.png'.format(infile[:-9]))
    
    canva_norm = ROOT.TCanvas('canva_norm', "", 100, 200, 700, 500)
    canva_norm.cd()
    g_norm.Draw('AP4C')
    canva_norm.SaveAs('{}_norm_ST.png'.format(infile[:-9]))
