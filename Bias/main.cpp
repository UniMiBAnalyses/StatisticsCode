/*
c++ -o main `root-config --cflags --glibs` -lRooFit  -lRooFitCore main.cpp
*/

#include <iostream>
#include <cstdlib>
#include <ctime>
#include <vector>
#include <math.h>

#include "TCanvas.h"
#include "TH1F.h"
#include "TGraph.h"
#include "TGraphErrors.h"
#include "TF1.h"
#include "TLegend.h"
#include "TFitResult.h"
#include "RooRealVar.h"
#include "RooConstVar.h"
#include "RooGaussian.h"
#include "RooArgusBG.h"
#include "RooAddPdf.h"
#include "RooDataSet.h"
#include "RooPlot.h"
#include "RooFitResult.h"

using namespace RooFit ;
using namespace std ;

int main (int argc, char ** argv)
{

  int steps = 10 ;
  int Ntoys = 100 ;
  if (argc > 1) 
    {
      steps = atoi (argv[1]) ;
    }

  //PG prepare basic components
  //PG ---- ---- ---- ---- ---- ---- ---- ---- ---- 

  RooRealVar mes ("mes", "m_{ES} (GeV)", 5.20, 5.30) ;

  //PG the variables and PDFs for the fit
  //PG ---- ---- ---- ---- ---- ---- ---- ---- ---- 

   // --- Parameters ---
  RooRealVar sigmean ("sigmean", "B^{#pm} mass", 5.28, 5.20, 5.30) ;
  RooRealVar sigwidth ("sigwidth", "B^{#pm} width", 0.0027, 0.001, 1.) ;

  // --- Build Gaussian PDF ---
  RooGaussian signalModel ("signal", "signal PDF", mes, sigmean, sigwidth) ;

  // --- Build Argus background PDF ---
  RooRealVar argpar ("argpar", "argus shape parameter", -20.0, -100., -1.) ;
  RooArgusBG background ("background", "Argus PDF", mes, RooConst (5.291), argpar) ;

  // --- Construct signal+background PDF ---
  RooRealVar nsig ("nsig", "#signal events", 200, 0., 10000) ;
  RooRealVar nbkg ("nbkg", "#background events", 800, 0., 10000) ;

  //PG the variables and PDFs for the event generation
  //PG ---- ---- ---- ---- ---- ---- ---- ---- ---- 

  // --- Build Gaussian PDF for event generation ---
  RooRealVar sigmean_gen ("sigmean_gen", "B^{#pm} mass", 5.28, 5.20, 5.30) ;
  RooRealVar sigwidth_gen ("sigwidth_gen", "B^{#pm} width", 0.0027, 0.001, 1.) ;
  RooGaussian signalModel_gen ("signal_gen", "signal PDF", mes, sigmean_gen, sigwidth_gen) ;

  // --- Build Argus background PDF for event generation ---
  RooRealVar argpar_gen ("argpar_gen", "argus shape parameter", -20.0, -100., -1.) ;
  RooArgusBG background_gen ("background_gen", "Argus PDF", mes, RooConst (5.291), argpar_gen) ;

  // --- Construct signal+background PDF for event generation ---
  RooRealVar nsig_gen ("nsig_gen", "#signal events", 200, 0., 10000) ;
  RooRealVar nbkg_gen ("nbkg_gen", "#background events", 800, 0., 10000) ;

  //PG biaed signals injection test
  //PG ---- ---- ---- ---- ---- ---- ---- ---- ---- 

  TGraphErrors bias_B ; //PG bias wrt injected biased signal
  TGraphErrors bias_O ; //PG bias wrt pure component of the signal

  TCanvas c1 ;

  //PG loop on possible contaminations
  for (int i = 0 ; i <= steps ; ++i)
    {
      float fraction = i ; 
      fraction /= steps ;

      RooRealVar nsig_B ("nsig_B", "nsig_B", nsig_gen.getValV () * (1. - fraction), 0., 10000) ;
      RooRealVar nbkg_B ("nbkg_B", "nbkg_B", nsig_gen.getValV () * fraction, 0., 10000) ;
      RooAddPdf biased_signal ("biased_signal", "biased_signal", RooArgList (signalModel_gen, background_gen), RooArgList (nsig_B, nbkg_B)) ;
      //PG build the total model with the contaminated signal
      RooAddPdf biased_model ("biased_model", "biased_model", RooArgList (biased_signal, background_gen), RooArgList (nsig_gen, nbkg_gen)) ;

      //PG use N toy experiments
      float bias_B_ave = 0. ;
      float bias_B_var = 0. ;
      float bias_O_ave = 0. ;
      float bias_O_var = 0. ;

      //PG loop over toys
      for (int j = 0 ; j < Ntoys ; ++j)
        {

          //PG GENERATING
          //PG ---- ---- ---- ---- ---- ---- ---- ---- ---- 

          //PG build the contaminated signal
          //PG generate events with contaminated total model
          RooDataSet * biased_events = biased_model.generate (mes, 2000) ;
    
          //PG FITTING
          //PG ---- ---- ---- ---- ---- ---- ---- ---- ---- 
          //PG prepare the fitting model
    
          RooAddPdf model ("model", "g+a", RooArgList (signalModel, background), RooArgList (nsig, nbkg)) ;
          //PG fit model to the biased events
          RooFitResult * fitResult = model.fitTo (*biased_events) ;
//          fitResult->status () ;

          bias_B_ave += nsig.getValV () - biased_signal.getValV () ;
          bias_B_var += (nsig.getValV () - biased_signal.getValV ()) 
                         * (nsig.getValV () - biased_signal.getValV ()) ;

          bias_O_ave += nsig.getValV () * (1-fraction) - biased_signal.getValV () ;
          bias_O_var += (nsig.getValV () * (1-fraction) - biased_signal.getValV ())
                        * (nsig.getValV () * (1-fraction) - biased_signal.getValV ()) ;

          //PG example plot
          if (j == 0)
            {
              RooPlot * mesframe = mes.frame () ;
              biased_events->plotOn (mesframe) ;
              model.plotOn (mesframe) ;
              model.plotOn (mesframe, Components (background), LineStyle (ELineStyle::kDashed)) ;
        
              mesframe->Draw () ;
              TString canvasName = "example_" ;
              canvasName += i ;
              canvasName += ".png" ;
              c1.Print (canvasName, "png") ;
            }

        } //PG loop over toys

      bias_B_ave /= Ntoys ; 
      bias_B_var = bias_B_var / Ntoys - bias_B_ave * bias_B_ave ;
      bias_B.SetPoint (bias_B.GetN (), fraction, bias_B_ave) ;
      bias_B.SetPointError (bias_B.GetN () - 1, 0., sqrt (bias_B_var)) ;

      bias_O_ave /= Ntoys ; 
      bias_O_var = bias_O_var / Ntoys - bias_O_ave * bias_O_ave ;
      bias_O.SetPoint (bias_O.GetN (), fraction, bias_O_ave) ;
      bias_O.SetPointError (bias_O.GetN () - 1, 0., sqrt (bias_O_var)) ;

    } //PG loop on possible contaminations
   
  bias_B.SetMarkerStyle (4) ;
  bias_B.SetMarkerColor (kBlue + 2) ;
  bias_B.SetLineColor (kBlue + 2) ;
  bias_B.GetHistogram ()->GetXaxis ()->SetTitle ("bkg fraction in the biased signal model") ;
  bias_B.GetHistogram ()->GetYaxis ()->SetTitle ("difference wrt expected value") ;
  bias_O.SetMarkerStyle (23) ;
  bias_O.SetMarkerColor (kRed + 2) ;
  bias_O.SetLineColor (kRed + 2) ;

  bias_B.Draw ("ALP") ;
  bias_O.Draw ("LP") ;

  TLegend * legend = new TLegend (0.5,0.7,0.9,0.9) ;
  legend->AddEntry(&bias_B, "wrt the signal", "PL") ;
  legend->AddEntry(&bias_O, "wrt the real signal", "PL") ;
  legend->Draw();

  c1.Print ("biases.png", "png") ;

  return 0 ;
}