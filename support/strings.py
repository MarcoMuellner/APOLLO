import os
##CI
#commands
strCmdNewFrame = 'New Frame available'
strCmdNewClient = 'New Client connected'
strCmdClientSettingChanged = 'Client Setting Changed'
#OS
#Paths
strPathSettings = os.path.join(os.path.expanduser('~'),'LightCurveAnalyzer.cfg')
##GUI
#GUITypes
strGUITypeTextEdit = 'textEdit'
strGUITypeCheckBox = 'checkBox'
##settings
##GUINames
#StaticSettingsWidget
txtBtnConnect = 'Connect to server'
txtBtnDisconnect = 'Disconnect from server'
txtLabelIPAdress = 'IP Adress'
txtLabelPort = 'Port'
#StatusWidget
txtLabelStatusDescr = 'Software Status: '
txtStatusNotConnected ='Not connected'
txtStatusConnected = 'Connected'
styleNotConnected = 'color: red'
styleConnected = 'color: green'
#LogWidget
txtLabelLog ='Server Log'
#VideoWidget
txtLabelVideo = 'Videostream:'
#SettingOptions
strOptionName       = 'GUI Name'
strOptionType       = 'GUI Type'
strOptionSection    = 'GUI Section'
strOptionValue      = 'Value'

