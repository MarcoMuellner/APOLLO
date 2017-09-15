PRO priors_background, kic, NUMAX = numax
 ;+
 ; ---------------------------------------------------------------------
 ; Author: Kevin Fusshoeller
 ; email: fussi_fusshoeller@yahoo.de
 ; Created: April/May 2016 
 ; Last modified: June 2016
 ; CEA/IRFU/SAp/LDEE France
 ; ---------------------------------------------------------------------
 
 ; ---------------------------------------------------------------------
 ; PURPOSE: 
 ;  Create all the files needed for the background fitting of a red giant (RG) using DIAMONDS.
 ; ---------------------------------------------------------------------

 ; ---------------------------------------------------------------------
 ; USAGE: 
 ;  Creates all the files needed for the background fitting of a RG using DIAMONDS and the ouputs
 ;  of the acf methodology.
 ; Parameters: 
 ;   - <kic>: The kic ID of the RG to be fitted.
 ; NEEDED: 
 ;   - a file containing the power spectrum density (PSD) of the red giant.
 ;   - a file containing the results of the 'acf.pro' procedure.
 ; ---------------------------------------------------------------------
 ;-

 ; Define some directories and check the kic
 input_dir = '/Users/kfusshoe/STAGE_2016/Depressed_Dipoles/SRGs/Results/'
 psd_dir = '/Users/kfusshoe/STAGE_2016/Depressed_Dipoles/SRGs/LC_CORR_FILT_INP'
 kic = STRCOMPRESS(STRING(kic), /REMOVE_ALL)
 IF STRLEN(kic) EQ 7 THEN BEGIN
    kic = '00' + kic 
 ENDIF ELSE BEGIN
    IF STRLEN(kic) EQ 8 THEN kic = '0' + kic
 ENDELSE

 ; Find and read the file containing the results of acf.pro
 name_star = FILE_SEARCH(input_dir, '*' + kic + '*', /EXPAND_ENVIRONMENT) 
 RESTORE, name_star
 
 ; Find and read the PSD
 name_file = FILE_SEARCH(psd_dir, '*' + kic + '*', /EXPAND_ENVIRONMENT) 
 power_crv = READFITS(name_file[0])
 freq = REFORM(power_crv[0,*])
 psd = REFORM(power_crv[1,*]) 

 nu_acf = nu_acf * 10.0^6
 
 ; Define the Oscillation params priors
 IF nu_acf LT 60 THEN BEGIN
    nu_max = (nu_acf / 0.8717)^(1.0 / 0.9068)
 ENDIF ELSE BEGIN
    interesting_zone = WHERE(freq * 10.0^6 GT nu_acf)
    max = MAX(psd(interesting_zone))
    nu_max = freq(WHERE(psd EQ max))*1.0e6
 ENDELSE
 IF KEYWORD_SET(NUMAX) THEN nu_max = numax

 lower_nu_max = 0.8 * nu_max
 upper_nu_max = 1.2 * nu_max

 dnu = 135 * (nu_max / 3050.0)^0.8

 sigma = 2 * dnu
 lower_sigma = 0.5 * dnu
 upper_sigma = 2.5 * dnu

 freqbin = (freq[1] - freq[0]) * 10.0^6
 width = dnu / freqbin
 psd_smth = SMOOTH(psd, width, /edge_truncate)
 interesting_zone = WHERE(freq * 10.0^6 GT nu_acf)
 height = MAX(psd_smth(interesting_zone))
 lower_height = 0.25 * height
 upper_height = 1.50 * height

 ; Define the priors for the white noise
 IF nu_acf GE 75.0 THEN BEGIN 
    white_noise_array = psd(WHERE(freq * 10.0^6 GT DOUBLE(nu_max + 3.0 * dnu, 0)))
 ENDIF ELSE BEGIN
    white_noise_array = psd(WHERE(freq * 10.0^6 GT 150))
 ENDELSE
 white_noise = MEAN(white_noise_array)
 lower_white_noise = 0.25 * white_noise 
 upper_white_noise = 1.50 * white_noise 

 ; Define the priors for the colored noise
 IF nu_max GT 7 THEN BEGIN 
    nu_color = 7 
 ENDIF ELSE BEGIN
    nu_color = nu_max
 ENDELSE
 lower_nu_color = 0.01
 upper_nu_color = nu_color 

 amp_color = amp_flic
 lower_amp_color = 0.01
 upper_amp_color = 0.20 * amp_flic 

 ; Define the priors for the rotation
 nu_rot = nu_acf 
 lower_nu_rot = 0.01 
 IF nu_acf GT 7 THEN BEGIN 
    upper_nu_rot = 7 
 ENDIF ELSE BEGIN
    upper_nu_rot = nu_acf
 ENDELSE
 amp_rot = amp_flic
 lower_amp_rot = 0.1
 upper_amp_rot = 1.0 * amp_flic 

 ; Define the priors for the first Granulation
 nu_g1 = 0.317 * nu_max^(0.970)
 lower_nu_g1 = 0.25 * nu_g1 
 upper_nu_g1 = 1.5 * nu_g1

 amp_g1 = 3383 * nu_max^(-0.609)
 lower_amp_g1 = 0.5 * amp_g1
 upper_amp_g1 = 1.5 * amp_g1 

 ; Define the priors for the second Granulation 
 nu_g2 = 0.948 * nu_max^(0.992)
 lower_nu_g2 = 0.5 * nu_g2 
 upper_nu_g2 = 1.75 * nu_g2

 amp_g2 = 3383 * nu_max^(-0.609)
 lower_amp_g2 = 0.25 * amp_g2
 upper_amp_g2 = 1.75 * amp_g2 

 ; Checks of no overlap 
 IF upper_nu_g1 GT lower_nu_g2 + 4 THEN BEGIN
    difference = upper_nu_g1 - lower_nu_g2
    upper_nu_g1 -= 0.5 * difference
    lower_nu_g2 += 0.5 * difference
    PRINT, 'difference g1-g2= ', difference
 ENDIF
 IF upper_nu_rot GT lower_nu_g1 + 3 THEN BEGIN
    difference = upper_nu_rot - lower_nu_g1
    upper_nu_rot -= 0.5 * difference
    lower_nu_g1 += 0.5 * difference
    PRINT, 'difference rot-g1= ', difference
 ENDIF

 ; Resume in two arrays
 boundaries = [lower_white_noise, upper_white_noise, lower_amp_color, upper_amp_color, lower_nu_color, upper_nu_color, $
 lower_amp_rot, upper_amp_rot, lower_nu_rot, upper_nu_rot, lower_amp_g1, upper_amp_g1, lower_nu_g1, upper_nu_g1, lower_amp_g2, upper_amp_g2, $
 lower_nu_g2, upper_nu_g2, lower_height, upper_height, lower_nu_max, upper_nu_max, lower_sigma, upper_sigma]
 

 ; Write an ASCII file for the priors.
 output_dir = '/Users/kfusshoe/github/Background/results/KIC' + kic + '/'
 IF FILE_TEST(output_dir, /DIRECTORY) EQ 0 THEN FILE_MKDIR, output_dir, /NOEXPAND_PATH
 data_dir = '/Users/kfusshoe/github/Background/data/'
 filename = output_dir + 'background_hyperParameters.txt'
 GET_LUN, lun1
 OPENW, lun1, filename
 PRINTF, lun1, '# Hyper parameters used for setting up uniform priors.', FORMAT = '(A0)'
 PRINTF, lun1, '# Each line corresponds to a different free parameter (coordinate).', FORMAT = '(A0)'
 PRINTF, lun1, '# Column #1: Minima (lower boundaries)', FORMAT = '(A0)'
 PRINTF, lun1, '# Column #2: Maxima (upper boundaries)', FORMAT = '(A0)'
 PRINTF, lun1, boundaries, FORMAT = '(F0.6, F15.6)'
 FREE_LUN, lun1
 
 ; Write an ASCII file for the PSD.
 filename = data_dir + 'KIC' + kic + '.txt'
 GET_LUN, lun2
 OPENW, lun2, filename
 FOR i=0L,n_elements(freq)-1 DO BEGIN
    PRINTF,lun2,freq(i)*1e6,psd(i),FORMAT = '(F0.6, F20.6)'
 ENDFOR
 FREE_LUN, lun2

 ; Write an ASCII file for the nested sampler configuring parameters.
 filename = output_dir + 'NSMC_configuringParameters.txt'
 NSMC_array = [500, 500, 10000, 1500, 50, 2.1, 0.01, 0.01]
 GET_LUN, lun3
 OPENW, lun3, filename
 PRINTF, lun3, NSMC_array, FORMAT = '(F0.6)'
 FREE_LUN, lun3
 
 ; Write a file with the value of the Nyquist
 filename = output_dir + 'NyquistFrequency.txt'
 GET_LUN, lun4
 OPENW, lun4, filename
 PRINTF, lun4, 283.2116656017908, FORMAT = '(F0.6)'
 FREE_LUN, lun4

; Write a file with the parameters for the X means clustering algorithm.
 filename = output_dir + 'Xmeans_configuringParameters.txt'
 xmeans_array = [1, 10]
 GET_LUN, lun5
 OPENW, lun5, filename
 PRINTF, lun5, xmeans_array, FORMAT = '(F0.6)'
 FREE_LUN, lun5

 stop

END
