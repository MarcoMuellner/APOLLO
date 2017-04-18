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
#strDataSettings
strSectBackgroundResPath   = 'Background Results Path'
strSectBackgroundDataPath   = 'Background Data Path'
#SettingOptions
strOptionName       = 'GUI_Name'
strOptionType       = 'GUI_Type'
strOptionSection    = 'GUI Section'
strOptionValue      = 'Value'
#ParameterSummaryStrings
strSummaryMean = "I Moment (Mean)"
strSummaryMedian = "Median"
strSummaryMode = "Mode"
strSummaryIIMoment = "II Moment (Variance if Normal distribution)"
strSummaryLowCredLim = "Lower Credible Limit"
strSummaryUpCredlim = "Upper Credible Limit"
strSummarySkew = "Skewness"

