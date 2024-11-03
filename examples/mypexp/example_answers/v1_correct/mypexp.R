## This is an example that gives a correct answer
mypexp <- function(x, rate, lower.tail, log.p) {
  if ( lower.tail ) {
    if ( log.p ) {
       if ( x*rate > 10 ) {
         return( -exp(-rate*x) ) 
       }
       else {
         return( log(-expm1(-rate*x) ) )
      }
    } else {
       return( -expm1(-rate*x) )
    }
  } else {
    if ( log.p ) {
       return( -rate*x )
    } else {
       return( exp(-rate*x) )
    }
  }
}
