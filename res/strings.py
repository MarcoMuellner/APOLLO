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
strSectIterativeRun = 'Iterative Run'
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
strSectOnlyResultsNeeded = "Only results needed"
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
strLightInterpolating = 'interpolating'
#StartypeValues
strStarTypeYoungStar = 'Young Star'
strStarTypeRedGiant = 'Red Giant'
#Fit Mode values
strRunIDFull = ' Full Background Model'
strRunIDNoise = 'Noise Background Model'
strRunIDBoth = 'Bayesian Evidence mode (both models and comparison)'
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
strPriorAmpHarvey1 = "a_1"
strPriorFreqHarvey1 = "b_1"
strPriorAmpHarvey2 = "a_2"
strPriorFreqHarvey2 = "b_2"
strPriorAmpHarvey3  = "a_3"
strPriorFreqHarvey3 = "b_3"
strPriorHeight = "H_osc"
strPriorNuMax = "nu_max"
strPriorSigma = "sigma_env"
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
strDiModeNoise = "NoiseOnly"
strDiModeFull = "FullBackground"
#Models used for Diamonds
strDiIntModeNoise = "noise"
strDiIntModeFull = "standard"
#DiamondsBinaryNames
strDiBinary_standard = "background_standard_model"
strDiBinary_noise = "background_noise_only_model"
strDiBinary = "background"
#DiamondsErrorStrings
strDiamondsErrBetterLikelihood = "Can't find point with a better Likelihood"
strDiamondsErrCovarianceFailed = "Covariance Matrix decomposition failed"
strDiamondsErrAssertionFailed = "Assertion failed"
strDiamondsErrMatrixCompositionFailed = "Matrix decomposition failed."
strDiamondsErrAborted = "Aborted (core dumped)"
strDiamondsErrCoreDumped = "core dumped"
strDiamondsErrQuitting = "Quitting program."
strDiamondsErrSegmentation = "Segmentation fault (core dumped)"
#DiamondsStatus
strDiStatRunning = "Running ..."
strDiamondsStatusGood = "Good"
strDiamondsStatusLikelihood = "Failed/Couldn't find point with better likelihood"
strDiamondsStatusCovariance = "Failed/Covariance decomposition failed"
strDiamondsStatusAssertion = "Failed/Assertion failed"
strDiamondsStatusMatrixDecomp = "Matrix decomposition failed"
strDiamondsStatusTooManyRuns = "Failed/Too many runs"
strDiamondsStatusPriorsChanged = "Priors changed"
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

summaryValues = [
    strSummaryMean ,
    strSummaryMedian ,
    strSummaryMode ,
    strSummaryIIMoment ,
    strSummaryLowCredLim ,
    strSummaryUpCredLim ,
    strSummarySkew ,
]
