;+----------------------------------------------------------------------
; NAME:
;       trismooth
;
; PURPOSE:
;       Triangular smoothing of a vector, including points near the ends.
;
; CATEGORY:
;	Smoothing
;
; CALLING SEQUENCE:
;       SMOOTHED = trismooth( VECTOR, WINDOW_WIDTH )
;
; INPUTS:
;       VECTOR  = The vector to be smoothed
;       WINDOW_WIDTH = The full width of the window over which the weighted
;               average is determined for each point (if even, use window+1).
;
; KEYWORDS:
;	GAUSS - if set, weighting is gaussian, rather than triangular
;
; OUTPUT:
;       Function returns the smoothed vector
;
; SUBROUTINES CALLED:
;
; PROCEDURE:
;       Each point is replaced by triangular weighting of the nearest WINDOW of points.
;       The width of the window shrinks towards the ends of the vector.
;
;
; REVISION HISTORY:
;       Written, Bill Davis. 23-Mar-00, per Michael Bell
;-----------------------------------------------------------------------
FUNCTION trismooth, ARRAY, window_width, GAUSS=gauss, verbose=verbose

IF N_PARAMS(0) LT 2 THEN window_width = 5
   ; if even, use window_width+1
IF FIX(window_width)/2*2 EQ FIX(window_width) THEN window_width = window_width + 1

LEND = N_ELEMENTS(ARRAY)-1
IF (LEND+1) LT window_width THEN BEGIN
   if keyword_set( verbose ) then print,'trismooth:  vector too short'
   RETURN,ARRAY
ENDIF

IF KEYWORD_SET( gauss ) THEN BEGIN
   parms = [ 1.0, window_width/2, window_width/4]
   weights = GAUSSIAN( INDGEN(window_width), parms )
ENDIF ELSE BEGIN	; triangular weights
   halfWeights = INDGEN(window_width/2)
   weights = ([ halfWeights, window_width/2, REVERSE(halfWeights) ] + 1)
ENDELSE
tot = TOTAL(weights)

SMOOTHED = FLTARR(LEND+1)
OFFSET = FIX(window_width/2)
LOCAL  = FLTARR(window_width)


FOR I = long(OFFSET), long(LEND-OFFSET) DO BEGIN
   SMOOTHED(I) = TOTAL( ARRAY(I-OFFSET:I+OFFSET) * weights )
ENDFOR

smoothed = smoothed/tot

; Fix the ends:

FOR i = 0, offset-1 DO BEGIN
   SMOOTHED(I) = TOTAL( ARRAY(0:I+OFFSET) * weights(offset-i:*) ) / $
                 TOTAL( weights(offset-i:*) )
ENDFOR

FOR i = lend, lend-offset+1, -1 DO BEGIN
   SMOOTHED(i) = TOTAL( ARRAY(i-offset:*) * weights(0:offset+(lend-i)) ) / $
                 TOTAL( weights(0:offset+(lend-i)) )
ENDFOR

RETURN,SMOOTHED
END
