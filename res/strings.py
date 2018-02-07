import os
##OS
#Paths
strPathSettings = os.path.join(os.path.expanduser('~'),'lightCurveAnalyzer.json')
strPathDefSettings = 'res/default_settings.json'
##GUI
#GUITypes
strGUITypeTextEdit = 'textEdit'
##Settings
strDataSettings= 'Data Settings'
strCalcSettings= 'Calculation Settings'
strDiamondsSettings ='Diamonds Settings'
strMiscSettings = "Misc Settings"
#strDataSettings
strSectLightCurveAlgorithm = 'Refine lightcurves algorithm'
strSectDataRefinement = 'Refinement of Data'
strSectPowerMode = 'Mode used to calculate Powerspectra (scipy,numpy)'
strSectStarType= 'Star Type'
#strDiamondsSettings
strSectBackgroundDataPath   = 'Background Data Path'
strSectBackgroundResPath   = 'Background Results Path'
strSectDiamondsBinaryPath = 'Background binary path'
strSectFittingMode = 'Fitting mode'
strSectPyDIAMONDSRootPath = 'PyDIAMONDS root path'
strSectDiamondsRunMode = 'Diamonds run mode'
#strMiscSettings
strSectDevMode = "Developer Mode"
strSectAnalyzerResults = "Analyzer Results Path"
strSectForceDiamondsRun = "Force DIAMONDS run"
strSectRunBinaries = "Run Binaries"
#SettingOptions
strOptionName       = 'GUI_Name'
strOptionType       = 'GUI_Type'
strOptionSection    = 'GUI Section'
strOptionValue      = 'Value'
#SettingValues
strPowerModeNumpy = "numpy"
strPowerModeSciPy = 'scipy'
#Data Refinement values
strRefineNone = "None"
strRefineStray = "Remove Stray"
#LightcurveAlgorithmValues
strLightCutting = 'cutting'
strLightCombining = 'combining'
#StartypeValues
strStarTypeYoungStar = 'Young Star'
strStarTypeRedGiant = 'Red Giant'
#Fit Mode values
strFitModeFullBackground = ' Full Background Model'
strFitModeNoiseBackground = 'Noise Background Model'
strFitModeBayesianComparison = 'Bayesian Evidence mode (both models and comparison)'
#strSectDiamondsRunMode
strPythonMode = 'Python'
strCppMode = 'C++'
#ParameterSummaryStrings
strSummaryMean = "I Moment (Mean)"
strSummaryMedian = "Median"
strSummaryMode = "Mode"
strSummaryIIMoment = "II Moment (Variance if Normal distribution)"
strSummaryLowCredLim = "Lower Credible Limit"
strSummaryUpCredLim = "Upper Credible Limit"
strSummarySkew = "Skewness"
#EvidenceFileStrings
strEvidSkillLog = "Skilling's log(Evidence)"
strEvidSkillErrLog = "Skilling's Error log(Evidence)"
strEvidSkillInfLog = "Skilling's Information Gain"
strEvidSkillLogWithErr = "Skillings log with Error"
#PriorFileStrings
strPriorFlatNoise = "w"
strPriorAmpHarvey1 = "$\sigma_\mathrm{long}$"
strPriorFreqHarvey1 = "$b_\mathrm{long}$"
strPriorAmpHarvey2 = "$\sigma_\mathrm{gran,1}$"
strPriorFreqHarvey2 = "$b_\mathrm{gran,1}$"
strPriorAmpHarvey3  = "$\sigma_\mathrm{gran,2}$"
strPriorFreqHarvey3 = "$b_\mathrm{gran,2}$"
strPriorHeight = "$H_\mathrm{osc}$"
strPriorNuMax = "$f_\mathrm{max}$ "
strPriorSigma = "$\sigma_\mathrm{env}$"
#PriorFileUnits
strPriorUnitFlatNoise = "ppm$^2$/$\mu$Hz"
strPriorUnitAmpHarvey1 = "ppm"
strPriorUnitFreqHarvey1 = "$\mu$Hz"
strPriorUnitAmpHarvey2 = "ppm"
strPriorUnitFreqHarvey2 = "$\mu$Hz"
strPriorUnitAmpHarvey3  = "ppm"
strPriorUnitFreqHarvey3 = "$\mu$Hz"
strPriorUnitHeight = "ppm$^2$/$\mu$Hz"
strPriorUnitNuMax = "$\mu$Hz"
strPriorUnitSigma = "$\mu$Hz"
#DiamondsModes
strDiamondsModeNoise = "NoiseOnly"
strDiamondsModeFull = "FullBackground"
#DiamondsBinaryNames
strDiamondsExecNoise = "noiseBackground"
strDiamondsExecFull = "background"
#DiamondsErrorStrings
strDiamondsErrBetterLikelihood = "Can't find point with a better Likelihood"
strDiamondsErrCovarianceFailed = "Covariance Matrix decomposition failed"
strDiamondsErrAssertionFailed = "Assertion failed"
#DiamondsStatus
strDiamondsStatusRunning = "Running ..."
strDiamondsStatusGood = "Good"
strDiamondsStatusLikelihood = "Failed/Couldn't find point with better likelihood"
strDiamondsStatusCovariance = "Failed/Covariance decomposition failed"
strDiamondsStatusAssertion = "Failed/Assertion failed"
strDiamondsStatusTooManyRuns = "Failed/Too many runs"
#ResultsStringsPrefix
strAnalyzerResTypeYoungStar = "YS"
strAnalyzerResTypeRedGiant = "RG"
#ResultsStringsSectNames
strAnalyzerResSectNuMaxCalc = "NuMaxCalc"
strAnalyzerResSectDiamondsPriors = "Diamonds_Priors"
strAnalyseSectDiamonds = "Diamonds"
strAnalyzerResSectAnalysis = "Analysis"
#ResultStringsValNames
strAnalyzerResValBayes = "Bayes Factor"
strAnalyzerResValStrength = "Strength of evidence"
#strRootPath
ROOT_PATH = os.getcwd()
#Namelists
priorNames = [strPriorFlatNoise,
       strPriorAmpHarvey1,
       strPriorFreqHarvey1,
       strPriorAmpHarvey2,
       strPriorFreqHarvey2,
       strPriorAmpHarvey3,
       strPriorFreqHarvey3,
       strPriorHeight,
       strPriorNuMax,
       strPriorSigma]

priorUnits = [strPriorUnitFlatNoise,
           strPriorUnitAmpHarvey1,
           strPriorUnitFreqHarvey1,
           strPriorUnitAmpHarvey2,
           strPriorUnitFreqHarvey2,
           strPriorUnitAmpHarvey3,
           strPriorUnitFreqHarvey3,
           strPriorUnitHeight,
           strPriorUnitNuMax,
           strPriorUnitSigma]
