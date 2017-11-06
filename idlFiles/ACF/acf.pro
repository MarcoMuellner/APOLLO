FUNCTION sinc_and_sine, X, A
 ; ---------------------------------------------------------------------
 ; Function returning the values of the sum of a squared sinc- and a sine-function.
 ; ---------------------------------------------------------------------
 F = FLTARR(N_ELEMENTS(X))
 IF X(0) EQ 0.0 THEN BEGIN
    F(0) = 1.0
    X_new = X(1:N_ELEMENTS(X)-1)
    F(1:N_ELEMENTS(X)-1) = A[1] * (SIN(4 * !PI * X_new / A[0]))^2/(4 * !PI * X_new / A[0])^2 + A[2] * SIN(2 * !PI * 4 * X_new / A[0])
 ENDIF
 RETURN,F
END


FUNCTION sinc, X, A
 ; ---------------------------------------------------------------------
 ; Function returning the values of a squared sinc-function.
 ; ---------------------------------------------------------------------
 F = FLTARR(N_ELEMENTS(X))
 IF X(0) EQ 0.0 THEN BEGIN
    F(0) = 1.0
    X_new = X(1:N_ELEMENTS(X)-1)
    F(1:N_ELEMENTS(X)-1) = A[1] * SIN((4 * !PI * X_new / A[0])^2)/(4 * !PI * X_new / A[0])^2
 ENDIF
 RETURN,F
END


FUNCTION sine, X, A
 ; ---------------------------------------------------------------------
 ; Function returning the values of a sine-function.
 ; ---------------------------------------------------------------------
 F = A[1] * SIN(2 * !PI * 4 * X / A[0])
 RETURN,F
END


FUNCTION power_law, X, A
 F = A[0] * X^(A[1])
 RETURN, F
END


PRO acf, kic, filter, FILE_PSD = file_psd, PLOT_PSD = plot_psd, PLOT_ACF = plot_acf
 ;+
 ; ---------------------------------------------------------------------
 ; Author: Kevin Fusshoeller
 ; email: fussi_fusshoeller@yahoo.de
 ; Created: April 2016
 ; Last modified: August 2016
 ; CEA/IRFU/SAp/LDEE France
 ; ---------------------------------------------------------------------


 ; ---------------------------------------------------------------------
 ; PURPOSE:
 ; Read a lightcurve of a high cadence Kepler target and apply a high pass filtering
 ; at low frequencies to it. Then apply an auto-correlation to the Fourier transform
 ; of the filtered light curve to determine the timescale of the granulation and oscillation.
 ; For more details, look at Kallinger et Al (2016)
 ;
 ; Comments: -) The code exists in a clean form under the routines: A2ZP_ACF_method.pro and
 ;              A2ZP_numax_from_ACF.pro. However if you want to use my code to configure priors
 ;              for the background fitting using DIAMONDS, you have to use this code in combination with
 ;              the procedure 'acf_on_stars'. Apart from some less interesting parameters this, procedures
 ;              produces plots of the autocorrelation and the PSD.
 ;           -) Upon testing I realized that while fitting the squared of a sinc function fits the
 ;              autocorrelation better. However I don't think that it will affect the results
 ;              significantly.
 ; ---------------------------------------------------------------------

 ; ---------------------------------------------------------------------
 ; USAGE:
 ;   Returns the typical timescale of the granulation and the frequency of the filtering.
 ; Parameters:
 ;   - <kic>: an integer or a string describing the kic ID of the star, which
 ;     should be analyzed.
 ;   - <starnumber>: The number given to the star.
 ;   - <filter>: an integer giving the initial value of the filter. Unit: days
 ; Optional Keywords:
 ;   - <plot_psd>: set if you want the PSD to be plotted
 ;   - <plot_ACF>: set if you want the ACF to be plotted
 ; ---------------------------------------------------------------------
 ;-

 !p.multi=0
 !x.style = 1
 !y.style = 1
 ; ---------------------------------------------------------------------
 ; Check if KIC ID contains 9 digits
 ; ---------------------------------------------------------------------

 kic = STRCOMPRESS(STRING(kic),/remove_all)     ; If an integer, make it a string
 n_digits = STRLEN(kic)
 IF n_digits EQ 7 THEN BEGIN
 kic = '00' + kic
 ENDIF ELSE IF n_digits EQ 8 THEN BEGIN
    kic = '0' + kic
 ENDIF
 filter_string = STRCOMPRESS(STRING(filter), /REMOVE_ALL)

 ; ---------------------------------------------------------------------
 ; Set the input and output directories for data reading
 ; ---------------------------------------------------------------------
 ;starnumber = STRCOMPRESS(STRING(starnumber), /remove_all)
 input_dir = '/Users/Marco/Documents/LCA/idlFiles/ACF/LC/'
 psd_dir = '/Users/Marco/Documents/LCA/idlFiles/ACF/PSD/'
 output_dir = '/Users/Marco/Documents/LCA/idlFiles/ACF/RESULTS/'
 name = 'kplr*' + kic + '*COR_filt_inp.fits'

 ; Light_crv is a 2-colomn array, with time (unit of day) and amplitude (unit: ppm) being the 1st
 ; and 2nd colomn respectively

 light_crv = READFITS(input_dir + name)
 light_crv = [[light_crv[0,*]],light_crv[1,*]]
 ;readcol,input_dir+'KIC'+kic+'.txt',time_array,amp_array,format='d,d'

;light_crv = [[time_array],[amp_array]]
;light_crv = TRANSPOSE(light_crv)

 ; ---------------------------------------------------------------------
 ; Define some useful variables and convert array to vector
 ; ---------------------------------------------------------------------
 filter = FLOAT(filter)
 n_time_elements = (SIZE(light_crv))[2]
 ; Convert light curve array to two vectors
 time_array = REFORM(light_crv[0,*] - light_crv[0,0])
 amp_array = REFORM(light_crv[1,*])

 IF time_array(n_time_elements - 1) - time_array[0] LE filter THEN BEGIN
  PRINT, 'ERROR: Filter is bigger than observing time'
  STOP
  ;ACF = {ERROR: 1}
  ;RETURN, ACF
 ENDIF

 ; Convert time into units of s
 time_array *= 3600.0 * 24.0


 ; ---------------------------------------------------------------------
 ; Rebin data at 'filter' days while acounting for gaps.
 ; ---------------------------------------------------------------------
 timebin = MEAN(time_array[1:n_time_elements - 1] - time_array[0:n_time_elements - 2])
 normalized_bin_size = ROUND(filter * 24.0 * 3600.0 / FIX(timebin))
 n_bins = FIX(n_time_elements / normalized_bin_size)
 ; Find out how many points are left and give its prime factors
 n_points_left = n_time_elements - normalized_bin_size * n_bins
 IF n_points_left GT 1 THEN BEGIN
    factor, n_points_left, prime_factors, prime_powers
    index_shift = prime_factors[0]^prime_powers[0]
    n_cols = n_points_left / index_shift + 1
 ENDIF ELSE BEGIN
    IF  n_points_left EQ 1 THEN BEGIN
        n_cols = 2
        index_shift = 1
    ENDIF ELSE BEGIN
        n_cols = 1
        index_shift = 0
    ENDELSE
 ENDELSE

 ; Define a matrix of amp_rebin-vectors shifted by a certain value, so that you include all the points
 ;amp_rebin_array = DBLARR(n_time_elements)
 ;n_points_per_bin_matrix = DBLARR(n_cols, n_time_elements)
 amp_mean_array = DBLARR(n_cols)
 FOR k = 0, n_cols - 1 DO BEGIN

    amp_rebin_array = DBLARR(n_time_elements - n_points_left)
    n_points_per_bin_array = DBLARR(n_time_elements - n_points_left)
    amp_substract_array = DBLARR(n_time_elements - n_points_left)
    i = LONG(k * index_shift)
    FOR j = 0, n_bins - 1 DO BEGIN
        bin_mean = 0.0
        ref_time = i
        count = 1

        WHILE (i LT n_time_elements - 1 AND (time_array[i] - time_array[ref_time]) / (3600.0 * 24.0) LT filter) DO BEGIN
            ;amp_rebin_array[j] += amp_array[i]
            bin_mean += amp_array[i]
            ; Account for gaps
            IF (amp_array[i] NE 0) THEN BEGIN
                count += 1
            ENDIF
            i += 1
        ENDWHILE

        ; Perform the last step ( i = n_time_elements - 1)
        bin_mean += amp_array[i]
        IF (amp_array[i] NE 0) THEN BEGIN
            count += 1
        ENDIF

        count_float = FLOAT(count)
        IF count GT 1 THEN BEGIN
            bin_mean /= (count_float - 1)
            ;amp_rebin_array[j] /= (count_float - 1)
        ENDIF
        amp_rebin_array[ref_time - k * index_shift : (i - 1) - k * index_shift] = bin_mean
        n_points_per_bin_array[ref_time - k * index_shift : (i - 1) - k * index_shift] = count
    ENDFOR

    amp_substract_array = amp_array[k * index_shift:k * index_shift + N_ELEMENTS(amp_rebin_array) - 1] - amp_rebin_array
    amp_substract_array = amp_substract_array(WHERE(n_points_per_bin_array GE normalized_bin_size / 2))
    amp_mean_array[k] = MEAN(amp_substract_array)
 ENDFOR

 print, 'loop ended correctly. Amp_mean_array = ', amp_mean_array


 ; ---------------------------------------------------------------------
 ; Determine the flicker amplitude
 ; ---------------------------------------------------------------------

 ; Substract smoothed light curve from original light curve
 ;amp_substract_array = amp_array - amp_rebin_array

 ; Define the mean amplitude
 ;amp_mean = MEAN(amp_substract_array)
 amp_mean = MEAN(amp_mean_array)

 ;print, 'amp_mean = ', amp_mean

 amp_substract_array = amp_substract_array(UNIQ(amp_substract_array))
 amp_flic = 0
 FOR i = 0L, N_ELEMENTS(amp_substract_array) - 1 DO BEGIN
    amp_flic += (amp_substract_array[i] - amp_mean)^2
 ENDFOR
 denominator = FLOAT(N_ELEMENTS(amp_substract_array))
 amp_flic = SQRT(amp_flic / denominator)

 print, 'flicker amplitude = ', amp_flic


 ; ---------------------------------------------------------------------
 ; Give a first rough value for the filtering frequency. Apply a triangular filter to the light
 ; curve
 ; ---------------------------------------------------------------------
 nu_filter = 10.0^(5.187) / (amp_flic^(1.560) * 10.0^6)

 print, 'First guess for filter = ', nu_filter

 ;stop
 ; Find the corresponding time-scale for smoothing
 tau_filter = 1.0 / nu_filter

 ; Perform the smoothing and filtering
 new_normalized_bin_size = ROUND(tau_filter/ timebin)
 new_n_bins = FIX(n_time_elements / new_normalized_bin_size)
 amp_smoothed_array = trismooth(light_crv, new_normalized_bin_size)
 amp_filtered_array = amp_array - amp_smoothed_array


 ; ---------------------------------------------------------------------
 ; Find the autocorrelation function (ACF)
 ; ---------------------------------------------------------------------
 ; Shift the time series using interpolation to create a lag with a smaller timestep
 length = LONG(1.5 * tau_filter * 4 / timebin)
 IF length GT n_time_elements THEN length = LONG(1.5 * 4 / (10.0^(-7) * timebin)) - 1
 IF length GT n_time_elements THEN length = n_time_elements - 1
 acf = DBLARR(length + 1)
 FOR j = 0L, length DO BEGIN
    time_shift = j / 4.0
    acf[j] = CORRELATE(amp_filtered_array, shift_interp(amp_filtered_array, time_shift), /DOUBLE)
 ENDFOR


 acf_square = acf^2


 ;loadct,39,/silent
 ;device,decomposed=8,retain=2,true_color=8


 ; Fit the ACF and find tau_acf
 tau_guess = DOUBLE(0.5 * tau_filter)
 A = [tau_guess, 1.0D, 0.05D]
 B = [tau_guess, 1.0d]
 parinfo = REPLICATE({fixed:0, limited:[0,0], limits:[0.d, 0.d]}, 3)
 parinfo[1].limited[0] = 1
 parinfo[1].limited[1] = 1
 parinfo[1].limits[0] = 0.8d
 parinfo[1].limits[1] = 1.2d
 parinfo[2].limited[0] = 1
 parinfo[2].limits[0] = 0.0d
 ;acf_fit = mpfitfun('sinc_and_sine', time_array, acf_square, err, A, PARINFO = parinfo)

 ; First fit a simple sinc function.
 acf_fit = mpfitfun('sinc', time_array[0:length]/4.0, acf_square, err, B, YFIT = sinc_fit)
 ; plot,time_array[0:length]/4.0,sinc_fit
 ; oplot,time_array[0:length]/4.0,acf_square,color=200
 stop


; Compute the residuals and fit a sine function to them.
 residuals = acf_square - sinc_fit
 ;C = [acf_fit[0], 0.05D]
 scaled_time_array = time_array / (acf_fit[0])
 cut = time_array(WHERE(scaled_time_array LE 2.0))/4.0
 residuals = residuals(WHERE(scaled_time_array LE 2.0))
 ;res_fit = mpfitfun('sine', cut, residuals, err, C, YFIT = sine_fit)
 res_fit = POLY_FIT(cut, residuals, 4, YFIT = polyfit)

; Substract the sine function from the ACF and redo the fitting
 acf_adjusted = acf_square(WHERE(scaled_time_array LE 1.5)) - polyfit
 adjusted_acf_fit = mpfitfun('sinc', cut, acf_adjusted, err, acf_fit, YFIT = adjusted_fit)

 tau_acf = adjusted_acf_fit[0] / (4.0)

 PRINT, 'First Guess for autocorrelation timescale = ', tau_acf / 60.0, ' mins'


 ; ---------------------------------------------------------------------
 ; Improve the estimate of tau_filter
 ; ---------------------------------------------------------------------
 ; Change units of tau_acf to minutes for the next formula
 tau_acf_minutes = tau_acf / 60.0
 nu_filter = 10.0^(3.098) * 1.0 / (tau_acf_minutes^(0.932)) * 1.0 / (tau_acf_minutes^(0.05)) ; nu_filter is in muHz

 ; Change units of nu_filter to Hz
 nu_filter = nu_filter * 10.0^(-6)
 tau_filter = 1.0 / nu_filter

 PRINT, 'New filter = ', nu_filter


 ; ---------------------------------------------------------------------
 ; Recompute the same steps as before
 ; ---------------------------------------------------------------------

; Perform the smoothing and filtering
 new_normalized_bin_size = ROUND(tau_filter/ timebin)
 new_n_bins = FIX(n_time_elements / new_normalized_bin_size)
 amp_smoothed_array = trismooth(light_crv, new_normalized_bin_size)
 amp_filtered_array = amp_array - amp_smoothed_array


  ; Shift the time series using interpolation to create a lag with a smaller timestep
 length = LONG(1.5 * tau_filter * 4 / timebin)
 IF length GT n_time_elements THEN length = LONG(1.5 * 4 / (10.0^(-7) * timebin)) - 1
 IF length GT n_time_elements THEN length = n_time_elements - 1
 acf = DBLARR(length + 1)
 FOR j = 0L, length DO BEGIN
    time_shift = j / 4.0
    acf[j] = CORRELATE(amp_filtered_array, shift_interp(amp_filtered_array, time_shift), /DOUBLE)
 ENDFOR
 acf_square = acf^2


 ; Fit the ACF and find tau_acf
 ;acf_fit = mpfitfun('sinc_and_sine', time_array(test_lag_array), acf_square, err, acf_fit)

 ; First fit a simple sinc function.
 acf_fit = mpfitfun('sinc', time_array[0:length]/4.0, acf_square, err, adjusted_acf_fit, YFIT = sinc_fit)

 ; Compute the residuals and fit a sine function to them.
 residuals = acf_square - sinc_fit
 scaled_time_array = time_array / (acf_fit[0])
 cut = time_array(WHERE(scaled_time_array LE 1.5))/4.0
 residuals = residuals(WHERE(scaled_time_array LE 1.5))
 ;res_fit = mpfitfun('sine', cut, residuals, err, C, YFIT = sine_fit)
 res_fit = POLY_FIT(cut, residuals, 4, YFIT = polyfit)

 ; Substract the sine function from the ACF and redo the fitting
 acf_adjusted = acf_square(WHERE(scaled_time_array LE 1.5)) - polyfit
 adjusted_acf_fit = mpfitfun('sinc', cut, acf_adjusted, err, acf_fit, YFIT = adjusted_fit)

 tau_acf = adjusted_acf_fit[0]
 nu_acf = 1 / tau_acf

 print, 'Final estimation of nu_acf = ', nu_acf

 final_residuals = acf_adjusted - adjusted_fit

 ; Read the PSD file
 name = 'kplr' + kic + '*COR_PSD_filt_inp.fits'
 power = READFITS(psd_dir + name)
 freq = REFORM(power[0,*])
 power1 = REFORM(power[1,*])

 ; Find nu_max
 nu_max_init = (nu_acf * 1.0e6 / 1.1261)^(1.0 / 0.8352)
 dnu = 135 * (nu_max_init / 3050.0)^0.8

 freqbin = (freq[1] - freq[0]) * 1.0e6
 width = 2 * dnu / freqbin
 psd_smth = SMOOTH(power1, width, /EDGE_TRUNCATE)

 interesting_zone = WHERE(freq GT nu_acf)
 ; 1st method
 max1 = MAX(psd_smth(interesting_zone))
 nu_max1 = freq(WHERE(psd_smth EQ max1))
 ; 2nd method
 fit_zone = WHERE(freq GT nu_acf)
 new_freq = freq(fit_zone)
 A = [1.0, -1.0]
 background_fit = MPFITFUN('power_law', new_freq, psd_smth(fit_zone), err, A, YFIT = background)
 new_psd_smooth = psd_smth(fit_zone) - background
 new_interesting_zone = WHERE(new_freq GT nu_acf)
 max2 = MAX(new_psd_smooth(new_interesting_zone))
 nu_max2 = new_freq(WHERE(new_psd_smooth EQ max2))
 ; 3rd method
 IF N_ELEMENTS(power1) GT width + 2000 THEN $
     psd_smth3 = SMOOTH(power1, width + 2000, /EDGE_TRUNCATE) $
 ELSE $
     psd_smth3 = SMOOTH(power1, N_ELEMENTS(power1)/2, /EDGE_TRUNCATE)
 ratio = psd_smth(interesting_zone)/psd_smth3(interesting_zone)
 max3 = MAX(ratio)
 nu_max3 = new_freq(WHERE(ratio EQ max3))
 ;stop
 ;PRINT, nu_max1, nu_max2, nu_max3


 IF KEYWORD_SET(plot_psd) EQ 1 THEN BEGIN
     ; Plot the lightcurve and the PSD
    nu_letter = '$\nu$'
    mu_letter = '$\mu$'
    tau_letter = '$\tau$'
    x_str = 'Frequency ($\mu$Hz)'
    y_str = 'ppm!U2!n'
    y_str = 'PSD ('+y_str + '/$\mu$Hz)'
    str1 ="tau"
    filter = STRCOMPRESS(STRING(FIX(filter)), /REMOVE_ALL)

    IF FILE_TEST(output_dir + 'Figures/', /DIRECTORY) EQ 0 THEN FILE_MKDIR, output_dir + 'Figures/', /NOEXPAND_PATH
    filename = output_dir + 'Figures/' + 'KIC' + kic + '_full_PSD.eps'
    SET_PLOT, 'PS'
    ;WINDOW, DIMENSIONS = [1000, 400], /BUFFER
    DEVICE, FILENAME = filename, XS = 25, YS = 10, /COLOR, /ENCAPSULATED
    !p.multi=[0,2,1]
    PLOT, time_array/(3600.0*24.0), amp_array/amp_mean, XTITLE = 'Period (Days)', YTITLE = 'Relative Brightness (ppt)', XR = [0, 200],$
    POSITION = [0.15,0.25,0.48,0.9]
    ;PLOT, time_array/(3600.0*24.0), amp_array/amp_mean, XTITLE = 'Period (Days)', YTITLE = 'Relative Brightness (ppt)', $
    ;XR = [0, MAX(time_array/(3600.0*24.0))], POSITION = [0.12,0.1,0.48,0.95], /CURRENT, /BUFFER
    loadct, 5
    OPLOT, time_array/(3600.0*24.0), amp_smoothed_array/amp_mean, COLOR = 240, THICK = 2
    ;PLOT, time_array/(3600.0*24.0), amp_smoothed_array/amp_mean, COLOR = 'blue', THICK = 2, /CURRENT, /OVERPLOT, /BUFFER
    PLOT, power[0,*]*1e6, power[1,*], /XLOG, /YLOG, XTITLE = x_str, YTITLE = y_str, position = [0.63,0.25,0.95,0.9]
    ;PLOT, power[0,*]*1e6, power[1,*], /XLOG, /YLOG, XTITLE = x_str, YTITLE = y_str, XR = [MIN(power[0,*]), MAX(power[0,*])] *1.0e6, $
    ;position = [0.62,0.1,0.97,0.95], /CURRENT, /BUFFER
    ;loadct, 5
    OPLOT, [nu_acf, nu_acf]*1e6, [0.00001, 10e10], COLOR = 60
    ;PLOT, [nu_acf, nu_acf]*1e6, [0.00001, 10e10], COLOR = 'red', NAME = nu_letter + '!DACF', /CURRENT, /OVERPLOT, /BUFFER
    OPLOT, [nu_filter, nu_filter]*1e6, [0.00001, 10e10], COLOR = 110
    ;PLOT, [nu_filter, nu_filter]*1e6, [0.00001, 10e10], COLOR = 'blue', NAME = nu_letter + '!Dfilter', /CURRENT, /OVERPLOT, /BUFFER
    loadct,39,/silent
    OPLOT, [nu_max1, nu_max1]*1e6, [0.00001, 10e10], COLOR = 140, LINESTYLE = 2, THICK=3
    OPLOT, [nu_max2, nu_max2]*1e6, [0.00001, 10e10], COLOR = 190, LINESTYLE = 2, THICK=3
    OPLOT, [nu_max3, nu_max3]*1e6, [0.00001, 10e10], COLOR = 110, LINESTYLE = 2, THICK=3
    ;leg = LEGEND(TARGET = [p3,p4,p5,p6, p7], POSITION = [0.95, 0.88])
    loadct,0,/silent
    OPLOT, power[0,*]*1e6, psd_smth, COLOR = 150
    DEVICE,/CLOSE
    !p.multi = 0
 ENDIF

 IF KEYWORD_SET(plot_acf) EQ 1 THEN BEGIN
    ; Plot of the fits
    filename = output_dir + 'Figures/' + 'KIC' + kic + '_ACF.eps'
    scale = (tau_acf/4.0)
    ;WINDOW, DIMENSIONS = [640,640], /BUFFER
    DEVICE, FILENAME = filename, XS = 16, YS = 16, /COLOR, /ENCAPSULATED
    !p.multi = [0,1,3]
    loadct,39,/silent
    PLOT, cut/scale, acf_square(WHERE(scaled_time_array LE 1.5)), YTITLE = 'ACF!U2', POSITION = [0.1,0.55,0.9,0.95]
    ;PLOT, cut/scale, acf_square(WHERE(scaled_time_array LE 1.5)), XR = [cut[0] / scale, cut[N_ELEMENTS(cut) - 1] / scale], YTITLE = 'ACF!U2', $
    ;POSITION = [0.12,0.55,0.95,0.95], NAME = 'MEASURED ACF!U2', YR = [0, 1.0], /CURRENT, /BUFFER
    loadct, 5
    OPLOT, cut/scale, adjusted_fit, COLOR = 110
    ;PLOT, cut/scale, adjusted_fit, COLOR = 'blue', NAME = 'Simple Model', /CURRENT, /OVERPLOT, /BUFFER
    ;OPLOT, cut/scale, adjusted_fit + sine_fit, COLOR = 60
    ;PLOT, cut/scale, adjusted_fit + polyfit, COLOR = 'red', NAME = 'Complex Model', /CURRENT, /OVERPLOT, /BUFFER
    ;leg = LEGEND(TARGET = [p,p1,p2], POSITION = [0.85,0.85])
    PLOT, cut/scale, residuals(WHERE(scaled_time_array LE 1.5)), YTITLE = 'Residuals', position = [0.1,0.325,0.9,0.495]
    ;PLOT, cut/scale, residuals(WHERE(scaled_time_array LE 1.5)), XR = [cut[0] / scale, cut[N_ELEMENTS(cut) - 1] / scale] ,YTITLE = 'Residuals',$
    ;position = [0.12,0.325,0.95,0.495], /CURRENT, /BUFFER
    loadct, 1
    ;OPLOT, cut/scale, sine_fit, COLOR = 140
    ;PLOT, cut/scale, polyfit, COLOR = 'blue', NAME = 'Fit', /CURRENT, /OVERPLOT, /BUFFER
    ;leg1 = LEGEND(TARGET = [p4], POSITION = [0.85, 0.47])
    PLOT, cut/scale, final_residuals, XTITLE = 'Period in units of ' + str1 + '!DACF', YTITLE = 'Residuals (Adjusted model)',$
    position = [0.1,0.1,0.9,0.27]
    ;PLOT, cut/scale, final_residuals,  XR = [cut[0] / scale, cut[N_ELEMENTS(cut) - 1] / scale], $
    ;XTITLE = 'Period in units of ' + tau_letter + '!DACF', YTITLE = 'New Residuals', position = [0.12,0.1,0.95,0.27], /CURRENT, /BUFFER
    DEVICE, /CLOSE
    !p.multi = 0
 ENDIF

 ACF = {kic: kic, ERROR: 0, frequency:nu_acf, filter: nu_filter, acf_amplitude: adjusted_acf_fit[1], flicker: amp_flic, $
 nu_max1: nu_max1, nu_max2: nu_max2, nu_max3: nu_max3}

 ;RETURN, ACF
end
