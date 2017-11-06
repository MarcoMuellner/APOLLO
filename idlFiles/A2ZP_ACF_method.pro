FUNCTION sinc, X, A
 ; ---------------------------------------------------------------------
 ; Function returning the values of a sinc-function: sinc(x^2).
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


PRO A2ZP_ACF_method, filein, filter
; PRO A2ZP_ACF_method, light_crv, filter
 ;+
 ; ---------------------------------------------------------------------
 ; Author: Kevin Fusshoeller
 ; email: fussi_fusshoeller@yahoo.de
 ; Created: April 2016
 ; Last modified: July 2016
 ; CEA/IRFU/SAp/LDEE France
 ; ---------------------------------------------------------------------

 ; ---------------------------------------------------------------------
 ; PURPOSE:
 ; Read a lightcurve of a high cadence Kepler target and apply a high pass filtering
 ; at low frequencies to it. Then apply an auto-correlation to the Fourier transform
 ; of the filtered light curve to determine the timescale of the granulation and oscillation.
 ; For more details, look at Kallinger et Al (2016)
 ; ---------------------------------------------------------------------

 ; ---------------------------------------------------------------------
 ; USAGE:
 ;   Returns the typical timescale (frequency nu_acf) of the granulation and the frequency of the filtering.
 ; Parameters:
 ;   - <light_crv>: an array made of 2 colons containing the light curve of a star . The first colon contains the time values
 ;                  of the observations in the units of days. The 2nd colon corresponds values of the amplitude at the time
 ;                  of the observation. Unit: ppm
 ;   - <filter>: an integer giving the initial value of the filter. Unit: days
 ; Output: nu_acf in the units of Hz.
 ; ---------------------------------------------------------------------
 ;-


; KZ:
;filein='KIC008196817.txt'
;filein=' '
readmultiple,filein,data,dim=2
light_crv=dblarr(2,22273)
light_crv(0,*)=data.x1
light_crv(1,*)=data.x2

 ; ---------------------------------------------------------------------
 ; Define some useful variables and convert array to vector
 ; ---------------------------------------------------------------------
 filter = FLOAT(filter)
 time_array = REFORM(light_crv[0,*] - light_crv[0,0])
 amp_array = REFORM(light_crv[1,*])
 n_time_elements = N_ELEMENTS(time_array)

 ; ---------------------------------------------------------------------
 ; Check that the filter is not bigger than the total observing time
 ; ---------------------------------------------------------------------
 IF time_array(n_time_elements - 1) - time_array[0] LE filter THEN BEGIN
  PRINT, 'ERROR: Filter is bigger than observing time'
  ACF = {ERROR: 1}
  ;RETURN, ACF
 ENDIF


 ; ---------------------------------------------------------------------
 ; Define important parameters for the filtering
 ; ---------------------------------------------------------------------
 ; Convert time into units of s
 time_array *= 3600.0 * 24.0

 ; Find the new number of bins after the filter
 duty_cycle = MEAN(time_array[1:n_time_elements - 1] - time_array[0:n_time_elements - 2])
 normalized_bin_size = ROUND(filter * 24.0 * 3600.0 / FIX(duty_cycle))
 n_bins = FIX(n_time_elements / normalized_bin_size)

 ; Find out how many points are left
 n_points_left = n_time_elements - normalized_bin_size * n_bins

 ; Find the prime factors of this number and define an index shift to include those points.
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


 ; ---------------------------------------------------------------------
 ; Filter the light curve at 'filter' days (exclude time scales longer than 'filter' days) and find the mean
 ; of the filtered curve
 ; ---------------------------------------------------------------------
 ; Working: Apply the filter to the light curve. Than shift the light curve and apply the filter again. This
 ;          ensures that all the data points are accounted for. Take a mean at the end.
 ; ---------------------------------------------------------------------
 ; Define a vector amp_mean containing the mean value of the individual shifted filtered light curves.
 amp_mean_array = DBLARR(n_cols)
 FOR k = 0, n_cols - 1 DO BEGIN

    ; Define the array containing the values of the rebinned light curve
    amp_rebin_array = DBLARR(n_time_elements - n_points_left)

    ; Array containing the number of non_zero elements in each bin
    n_points_per_bin_array = DBLARR(n_time_elements - n_points_left)

    ; Create array containing the filtered curve
    amp_substract_array = DBLARR(n_time_elements - n_points_left)

    ; Rebinning
    i = LONG(k * index_shift)
    FOR j = 0, n_bins -1 DO BEGIN
        bin_mean = 0.0
        ref_time = i
        count = 1

        WHILE (i LT n_time_elements - 1 AND (time_array[i] - time_array[ref_time]) / (3600.0 * 24.0) LT filter) DO BEGIN
            bin_mean += amp_array[i]
            ; Account for gaps
            IF (amp_array[i] NE 0) THEN BEGIN
                count += 1
            ENDIF
            i += 1
        ENDWHILE

        ; Perform the last step (the loop stops at i = n_time_elements - 2)
        bin_mean += amp_array[i]
        IF (amp_array[i] NE 0) THEN BEGIN
            count += 1
        ENDIF

        count_float = FLOAT(count)
        IF count GT 1 THEN BEGIN
            bin_mean /= (count_float - 1)
        ENDIF

        ; Keep original length of light curve
        PRINT, "I"
        PRINT, i
        PRINT, "n_bins"
        PRINT, n_bins
        PRINT, "LOW"
        PRINT, ref_time - k * index_shift
        PRINT, "HIGH"
        PRINT, (i - 1) - k * index_shift
        PRINT, "Size"
        PRINT, SIZE(amp_rebin_array)
        a = SIZE(amp_rebin_array)
        PRINT, "A"
        PRINT,a[1]
        IF a[1] GT (i - 1) - k * index_shift THEN BEGIN
          IF (i - 1) - k * index_shift GT ref_time - k * index_shift  THEN BEGIN
            amp_rebin_array[ref_time - k * index_shift : (i - 1) - k * index_shift] = bin_mean
            n_points_per_bin_array[ref_time - k * index_shift : (i - 1) - k * index_shift] = count
          ENDIF
        ENDIF
    ENDFOR

    amp_substract_array = amp_array[k * index_shift:k * index_shift + N_ELEMENTS(amp_rebin_array) - 1] - amp_rebin_array
    ; only select bins with enough non_zero points
    amp_substract_array = amp_substract_array(WHERE(n_points_per_bin_array GE normalized_bin_size / 2))
    amp_mean_array[k] = MEAN(amp_substract_array)
 ENDFOR

 print, 'loop ended correctly.' ;Amp_mean_array = ', amp_mean_array


 ; ---------------------------------------------------------------------
 ; Determine the flicker amplitude
 ; ---------------------------------------------------------------------
 ; Define the mean amplitude
 amp_mean = MEAN(amp_mean_array)

 ;print, 'amp_mean = ', amp_mean

 ; Calculate flicker amplitude
 amp_substract_array = amp_substract_array(UNIQ(amp_substract_array))
 amp_flic = 0
 print, N_ELEMENTS(amp_substract_array)
 FOR i = 0., N_ELEMENTS(amp_substract_array) - 1 DO BEGIN
    amp_flic += (amp_substract_array[i] - amp_mean)^2
 ENDFOR
 denominator = FLOAT(N_ELEMENTS(amp_substract_array))
 amp_flic = SQRT(amp_flic / denominator)

 print, 'flicker amplitude = ', amp_flic


 ; ---------------------------------------------------------------------
 ; Give a first rough value for the filtering frequency. Apply a triangular filter to the light
 ; curve.
 ; ---------------------------------------------------------------------
; nu_filter = 10.0^(5.187) / (amp_flic^(1.560) * 10.0^6)
 nu_filter = 10.0^(5.187) / (amp_flic^(1.560) * 10.0^6)

 print, 'First guess for filter = ', nu_filter

 ; Find the corresponding time-scale for smoothing
 tau_filter = 1.0 / nu_filter

 ; Perform the smoothing and filtering
 new_normalized_bin_size = ROUND(tau_filter/ duty_cycle)
 stop
 amp_smoothed_array = TRISMOOTH(light_crv, new_normalized_bin_size)
 amp_filtered_array = amp_array - amp_smoothed_array


 ; ---------------------------------------------------------------------
 ; Find the autocorrelation function (ACF)
 ; ---------------------------------------------------------------------
 ; Method: only apply the autocorrelation to the first few points, as we are only interested in the sinc function
 ;         and not in the points coming after it. Furthermore we interpolate the data, in order to get a smaller
 ;         time step and thus more points.
 ; ---------------------------------------------------------------------
 ; Determine the range to which to apply the autocoreelation
 length = LONG(1.5 * tau_filter * 4 / duty_cycle)
 IF length GT n_time_elements THEN length = LONG(1.5 * 4 / (10.0^(-7) * duty_cycle)) - 1
 IF length GT n_time_elements THEN length = n_time_elements - 1
 ; Perform the autocorrelation using interpolation.
 acf = DBLARR(length + 1)
 FOR j = 0L, length DO BEGIN
    time_shift = j / 4.0
    acf[j] = CORRELATE(amp_filtered_array, shift_interp(amp_filtered_array, time_shift), /DOUBLE)
 ENDFOR

 acf_square = acf^2


 ; ---------------------------------------------------------------------
 ; Fit the autocorrelation and determine tau_acf
 ; ---------------------------------------------------------------------
 ; First fit a simple sinc function.
 tau_guess = DOUBLE(0.5 * tau_filter)
 guess = [tau_guess, 1.0d]
 acf_fit = MPFITFUN('sinc', time_array[0:length]/4.0, acf_square, err, guess, YFIT = sinc_fit)

 ; Compute the residuals and fit a sine function (or polynomial of 4th degree) to them.
 residuals = acf_square - sinc_fit
 scaled_time_array = time_array / (acf_fit[0])
 cut = time_array(WHERE(scaled_time_array LE 2.0))/4.0
 residuals = residuals(WHERE(scaled_time_array LE 2.0))
 guess = [acf_fit[0], 0.05D]
 res_fit = MPFITFUN('sine', cut, residuals, err, guess, YFIT = sine_fit)
 ;res_fit = POLY_FIT(cut, residuals, 4, YFIT = polyfit)

 ; Substract the sine function from the ACF and redo the fitting
 acf_adjusted = acf_square(WHERE(scaled_time_array LE 1.5)) - sine_fit
 ;acf_adjusted = acf_square(WHERE(scaled_time_array LE 1.5)) - polyfit
 adjusted_acf_fit = MPFITFUN('sinc', cut, acf_adjusted, err, acf_fit, YFIT = adjusted_fit)

 ; First guess for tau_acf
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
 new_normalized_bin_size = ROUND(tau_filter/ duty_cycle)
 amp_smoothed_array = TRISMOOTH(light_crv, new_normalized_bin_size)
 amp_filtered_array = amp_array - amp_smoothed_array


 ; Find the autocorrelation function
 length = LONG(1.5 * tau_filter * 4 / duty_cycle)
 IF length GT n_time_elements THEN length = LONG(1.5 * 4 / (10.0^(-7) * duty_cycle)) - 1
 IF length GT n_time_elements THEN length = n_time_elements - 1
 acf = DBLARR(length + 1)
 FOR j = 0L, length DO BEGIN
    time_shift = j / 4.0
    acf[j] = CORRELATE(amp_filtered_array, shift_interp(amp_filtered_array, time_shift), /DOUBLE)
 ENDFOR
 acf_square = acf^2

 ; First fit a simple sinc function.
 acf_fit = MPFITFUN('sinc', time_array[0:length]/4.0, acf_square, err, adjusted_acf_fit, YFIT = sinc_fit)

 ; Compute the residuals and fit a sine function to them.
 residuals = acf_square - sinc_fit
 scaled_time_array = time_array / (acf_fit[0])
 cut = time_array(WHERE(scaled_time_array LE 1.5))/4.0
 residuals = residuals(WHERE(scaled_time_array LE 1.5))
 guess = [acf_fit[0], 0.05D]
 res_fit = MPFITFUN('sine', cut, residuals, err, C, YFIT = sine_fit)
 ;res_fit = POLY_FIT(cut, residuals, 4, YFIT = polyfit)

 ; Substract the sine function from the ACF and redo the fitting
 acf_adjusted = acf_square(WHERE(scaled_time_array LE 1.5)) - sine_fit
 ;acf_adjusted = acf_square(WHERE(scaled_time_array LE 1.5)) - polyfit
 adjusted_acf_fit = MPFITFUN('sinc', cut, acf_adjusted, err, acf_fit, YFIT = adjusted_fit)
 final_residuals = acf_adjusted - adjusted_fit

 ; Final value of tau_acf
 tau_acf = adjusted_acf_fit[0]
 nu_acf = 1 / tau_acf

 print, 'Final estimation of nu_acf = ', nu_acf
 ;RETURN, nu_acf
END
