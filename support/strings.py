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
#strDataSettings
strSectBackgroundResPath   = 'Background Results Path'
strSectBackgroundDataPath   = 'Background Data Path'
strSectPowerMode = 'Mode used to calculate Powerspectra (scipy,numpy)'
strSectDiamondsBinaryPath = 'Diamonds binary path'
#SettingOptions
strOptionName       = 'GUI_Name'
strOptionType       = 'GUI_Type'
strOptionSection    = 'GUI Section'
strOptionValue      = 'Value'
#SettingValues
strPowerModeNumpy = "numpy"
strPowerModeSciPy = 'scipy'
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
#DiamondsBinaryNames
strDiamondsNoGaussian = "multirun_noise"
strDiamondsGaussian = "multirun"


