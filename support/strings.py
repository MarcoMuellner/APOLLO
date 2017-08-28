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
strSectDiamondsBinaryPath = 'Diamonds binary path'
strSectFittingMode = 'Fitting mode'
#strMiscSettings
strSectDevMode = "Developer Mode"
strSectAnalyzerResults = "Analyzer Results Path"
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
strFitModeFullBackground = 'Full Background Model'
strFitModeNoiseBackground = 'Noise Background Model'
strFitModeBayesianComparison = 'Bayesian Evidence mode (both models and comparison)'
#ParameterSummaryStrings
strSummaryMean = "I Moment (Mean)"
strSummaryMedian = "Median"
strSummaryMode = "Mode"
strSummaryIIMoment = "II Moment (Variance if Normal distribution)"
strSummaryLowCredLim = "Lower Credible Limit"
strSummaryUpCredlim = "Upper Credible Limit"
strSummarySkew = "Skewness"
#EvidenceFileStrings
strEvidenceSkillLog = "Skilling's log(Evidence)"
strEvidenceSkillErrLog = "Skilling's Error log(Evidence)"
strEvidenceSkillInfLog = "Skilling's Information Gain"
#PriorFileStrings
strPriorFlatNoise = "Flatnoiselevel"
strPriorAmpHarvey1 = "AmplitudeHarvey1"
strPriorFreqHarvey1 = "FrequencyHarvey1"
strPriorAmpHarvey2 = "AmplitudeHarvey2"
strPriorFreqHarvey2 = "FrequencyHarvey2"
strPriorAmpHarvey3  = "AmplitudeHarvey3"
strPriorFreqHarvey3 = "FrequencyHarvey3"
strPriorHeight = "HeightOscillation"
strPriorNuMax = "NuMax"
strPriorSigma = "Sigma"
#DiamondsModes
strDiamondsModeNoise = "NoiseOnly"
strDiamondsModeFull = "FullBackground"
#DiamondsBinaryNames
strDiamondsExecNoise = "noiseBackground"
strDiamondsExecFull = "background"
