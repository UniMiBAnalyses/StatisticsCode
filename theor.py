import ROOT
import sys
argv = sys.argv
sys.argv = argv[:1]
import optparse

if __name__ == '__main__':
    
    sys.argv = argv

    usage = 'usage: %prog [options]'
    parser = optparse.OptionParser(usage)

    parser.add_option('--cut'       , dest='cut'        , help='type of cut'            , default='jv')
    parser.add_option('--dynamic'   , dest='dynamic'    , help='dynamic cut variable'   , default='mjj')

    (opt, args) = parser.parse_args()
    
    print ''
    print '                 cut =', opt.cut
    print '             dynamic =', opt.dynamic
    
    f = ROOT.TFile('latino_WpWpJJ_EWK.root')
    t = f.Get('latino')

    presel = '(abs(std_vector_jet_eta[1])<5 && abs(std_vector_jet_eta[0])<5 \
    && metPfType1 > 30 \
    && std_vector_jet_pt[0]>30 && std_vector_jet_pt[1]>30 \
    && (abs((std_vector_lepton_eta[0] - (std_vector_jet_eta[0]+std_vector_jet_eta[1])/2)/detajj) < 0.5) \
    && (abs((std_vector_lepton_eta[1] - (std_vector_jet_eta[0]+std_vector_jet_eta[1])/2)/detajj) < 0.5) \
    && (std_vector_lepton_flavour[0] * std_vector_lepton_flavour[1]) > 0 \
    && veto_EMTFBug)'

    weights = '(baseW*GEN_weight_SM/abs(GEN_weight_SM)*puW*effTrigW \
    *bPogSF_CSVM*std_vector_lepton_recoW[0]*std_vector_lepton_recoW[1] \
    *std_vector_lepton_idisoWcut_WP_Tight80X[0]*std_vector_lepton_idisoWcut_WP_Tight80X[1] \
    *std_vector_lepton_promptgenmatched[0]*std_vector_lepton_promptgenmatched[1]*(std_vector_trigger_special[0] \
    *std_vector_trigger_special[1]*std_vector_trigger_special[2]*std_vector_trigger_special[3] \
    *std_vector_trigger_special[5])*(((std_vector_trigger_special[8]==-2.)*(std_vector_trigger_special[6] \
    *std_vector_trigger_special[7])) || ((! (std_vector_trigger_special[8]==-2.))*(std_vector_trigger_special[8] \
    *std_vector_trigger_special[9])))*((std_vector_lepton_flavour[0] * std_vector_lepton_flavour[1])>0)*1.067466)'

    hN = ROOT.TH1F('hN', '', 3, -0.5, 2.5)
    hD = ROOT.TH1F('hD', '', 3, -0.5, 2.5)
    gr = ROOT.TGraphAsymmErrors() 

    for i in range (0,10):
        if opt.cut == 'jv':
            x_cut = i
            cut = '(std_vector_jet_pt[2]<{})'.format(x_cut)
        elif opt.cut == 'cjv':
            x_cut = i
            cut = '(std_vector_jet_pt[2]<{} \
            || (std_vector_jet_pt[2]>={} \
            && std_vector_jet_eta[2] <  \
            ((std_vector_jet_eta[0]<std_vector_jet_eta[1])*std_vector_jet_eta[0]+(std_vector_jet_eta[0]>= \
            std_vector_jet_eta[1])*std_vector_jet_eta[1]) || std_vector_jet_eta[2] > \
            ((std_vector_jet_eta[0]<std_vector_jet_eta[1])*std_vector_jet_eta[1]+(std_vector_jet_eta[0]>= \
            std_vector_jet_eta[1])*std_vector_jet_eta[0]) ))'.format(x_cut)
        elif opt.cut == 'djv':
            x_cut = i*0.002
            cut = '(std_vector_jet_pt[2]<{}*{})'.format(x_cut,opt.dynamic)
        elif opt.cut == 'dcjv':
            x_cut = i*0.002
            cut = '(std_vector_jet_pt[2]<{}*{} \
            || (std_vector_jet_pt[2]>={}*{} \
            && std_vector_jet_eta[2] <  \
            ((std_vector_jet_eta[0]<std_vector_jet_eta[1])*std_vector_jet_eta[0]+(std_vector_jet_eta[0]>= \
            std_vector_jet_eta[1])*std_vector_jet_eta[1]) || std_vector_jet_eta[2] > \
            ((std_vector_jet_eta[0]<std_vector_jet_eta[1])*std_vector_jet_eta[1]+(std_vector_jet_eta[0]>= \
            std_vector_jet_eta[1])*std_vector_jet_eta[0]) ))'.format(x_cut,opt.dynamic)
        for j in range(0,9):
            t.Draw('1 >> hN', presel+'*'+weights+'*'+cut+'*(std_vector_LHE_weight[{}]/std_vector_LHE_weight[0])'.format(j))
            t.Draw('1 >> hD', presel+'*'+weights +'*(std_vector_LHE_weight[{}]/std_vector_LHE_weight[0])'.format(j))
            efficiency = hN.Integral() / hD.Integral()
            if j == 0:
                eff = efficiency
                effmax = efficiency
                effmin = efficiency
            if efficiency > effmax:
                effmax = efficiency
            if efficiency < effmin:
                effmin = efficiency
        gr.SetPoint(i, x_cut, eff)
        gr.SetPointEYlow(i, effmin)
        gr.SetPointEYhigh(i, effmax)
        
    gr.SetMarkerStyle(20)
    gr.SetMarkerColor(ROOT.kRed)
         
    canva = ROOT.TCanvas('canva', "", 100, 200, 700, 500)
    canva.cd()
    gr.Draw('AP')
    canva.SaveAs('efficiency.png')
