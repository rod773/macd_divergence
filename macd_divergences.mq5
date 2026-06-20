//+------------------------------------------------------------------+
//|                                       MACD_Divergences_Davidd.mq5|
//|                                       Converted from Pine Script |
//|                                       Original by @DaviddTech     |
//+------------------------------------------------------------------+
#property copyright   "Converted from Pine Script @DaviddTech"
#property link        ""
#property version     "1.00"
#property description "MACD Divergences - Regular & Hidden (Bull/Bear)"

#property indicator_separate_window
#property indicator_buffers 9
#property indicator_plots   5

//--- Plot 1: Histogram
#property indicator_type1   DRAW_COLOR_HISTOGRAM
#property indicator_color1  clrGreen,clrPaleGreen,clrPink,clrRed
#property indicator_label1  "Histogram"
//--- Plot 2: MACD Line
#property indicator_type2   DRAW_LINE
#property indicator_color2  clrDodgerBlue
#property indicator_width2  2
#property indicator_label2  "MACD"
//--- Plot 3: Signal Line
#property indicator_type3   DRAW_LINE
#property indicator_color3  clrOrange
#property indicator_width3  2
#property indicator_label3  "Signal"
//--- Plot 4: Bull Arrow
#property indicator_type4   DRAW_ARROW
#property indicator_color4  clrGreen
#property indicator_width4  3
#property indicator_label4  "Bull Div"
//--- Plot 5: Bear Arrow
#property indicator_type5   DRAW_ARROW
#property indicator_color5  clrRed
#property indicator_width5  3
#property indicator_label5  "Bear Div"

//--- inputs
input int                InpFastEMA       = 12;          // Fast Length
input int                InpSlowEMA       = 26;          // Slow Length
input int                InpSignalSMA     = 9;           // Signal Smoothing
input ENUM_MA_METHOD     InpMAType        = MODE_EMA;    // Oscillator MA Type
input ENUM_MA_METHOD     InpSignalMAType  = MODE_EMA;    // Signal Line MA Type
input bool               InpDontTouchZero = true;        // Don't touch the zero line?
input int                InpLbR           = 5;           // Pivot Lookback Right
input int                InpLbL           = 5;           // Pivot Lookback Left
input int                InpRangeUpper    = 60;          // Max of Lookback Range
input int                InpRangeLower    = 5;           // Min of Lookback Range
input bool               InpPlotBull      = true;        // Plot Bullish
input bool               InpPlotBear      = true;        // Plot Bearish
input bool               InpPlotHiddenBull= false;       // Plot Hidden Bullish
input bool               InpPlotHiddenBear= false;       // Plot Hidden Bearish
input bool               InpDisplayAlert  = true;        // Display Alert

//--- buffers
double histBuffer[];
double histColorBuffer[];
double macdBuffer[];
double signalBuffer[];
double bullDivBuffer[];
double bearDivBuffer[];
double bullHiddenBuffer[];
double bearHiddenBuffer[];
double oscBuffer[];

//--- handles
int    macdHandle = INVALID_HANDLE;
int    fastMAHandle = INVALID_HANDLE;
int    slowMAHandle = INVALID_HANDLE;
int    signalMAHandle = INVALID_HANDLE;

//--- globals
static datetime lastAlertTime = 0;

//+------------------------------------------------------------------+
int OnInit()
  {
//--- buffers mapping
   SetIndexBuffer(0, histBuffer, INDICATOR_DATA);
   SetIndexBuffer(1, histColorBuffer, INDICATOR_COLOR_INDEX);
   SetIndexBuffer(2, macdBuffer, INDICATOR_DATA);
   SetIndexBuffer(3, signalBuffer, INDICATOR_DATA);
   SetIndexBuffer(4, bullDivBuffer, INDICATOR_DATA);
   SetIndexBuffer(5, bearDivBuffer, INDICATOR_DATA);
   SetIndexBuffer(6, bullHiddenBuffer, INDICATOR_DATA);
   SetIndexBuffer(7, bearHiddenBuffer, INDICATOR_DATA);
   SetIndexBuffer(8, oscBuffer, INDICATOR_CALCULATIONS);

//--- arrow codes
   PlotIndexSetInteger(3, PLOT_ARROW, 233);
   PlotIndexSetInteger(4, PLOT_ARROW, 234);

//--- empty values
   PlotIndexSetDouble(0, PLOT_EMPTY_VALUE, 0.0);
   PlotIndexSetDouble(2, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(3, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(4, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(5, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(6, PLOT_EMPTY_VALUE, EMPTY_VALUE);
   PlotIndexSetDouble(7, PLOT_EMPTY_VALUE, EMPTY_VALUE);

//--- indicator name
   string name = StringFormat("MACD Divergences(%d,%d,%d)", InpFastEMA, InpSlowEMA, InpSignalSMA);
   IndicatorSetString(INDICATOR_SHORTNAME, name);
   IndicatorSetInteger(INDICATOR_DIGITS, _Digits + 2);

//--- create MA handles based on type
   if(InpMAType == MODE_EMA)
     {
      fastMAHandle = iMA(_Symbol, PERIOD_CURRENT, InpFastEMA, 0, MODE_EMA, PRICE_CLOSE);
      slowMAHandle = iMA(_Symbol, PERIOD_CURRENT, InpSlowEMA, 0, MODE_EMA, PRICE_CLOSE);
     }
   else
     {
      fastMAHandle = iMA(_Symbol, PERIOD_CURRENT, InpFastEMA, 0, MODE_SMA, PRICE_CLOSE);
      slowMAHandle = iMA(_Symbol, PERIOD_CURRENT, InpSlowEMA, 0, MODE_SMA, PRICE_CLOSE);
     }

   if(fastMAHandle == INVALID_HANDLE || slowMAHandle == INVALID_HANDLE)
     {
      Print("Failed to create MA handles");
      return(INIT_FAILED);
     }

   return(INIT_SUCCEEDED);
  }

//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
   if(fastMAHandle != INVALID_HANDLE) IndicatorRelease(fastMAHandle);
   if(slowMAHandle != INVALID_HANDLE) IndicatorRelease(slowMAHandle);
  }

//+------------------------------------------------------------------+
//| Find pivot low: returns index of pivot or -1                      |
//+------------------------------------------------------------------+
int FindPivotLow(const double &osc[], int start, int lbL, int lbR, int limit)
  {
   for(int i = start; i >= limit; i--)
     {
      if(i - lbL < 0 || i + lbR >= ArraySize(osc))
         continue;
      bool isPivotLow = true;
      for(int j = 1; j <= lbL; j++)
        {
         if(osc[i] > osc[i - j])
           {
            isPivotLow = false;
            break;
           }
        }
      if(!isPivotLow) continue;
      for(int j = 1; j <= lbR; j++)
        {
         if(osc[i] > osc[i + j])
           {
            isPivotLow = false;
            break;
           }
        }
      if(isPivotLow)
         return(i);
     }
   return(-1);
  }

//+------------------------------------------------------------------+
//| Find pivot high: returns index of pivot or -1                     |
//+------------------------------------------------------------------+
int FindPivotHigh(const double &osc[], int start, int lbL, int lbR, int limit)
  {
   for(int i = start; i >= limit; i--)
     {
      if(i - lbL < 0 || i + lbR >= ArraySize(osc))
         continue;
      bool isPivotHigh = true;
      for(int j = 1; j <= lbL; j++)
        {
         if(osc[i] < osc[i - j])
           {
            isPivotHigh = false;
            break;
           }
        }
      if(!isPivotHigh) continue;
      for(int j = 1; j <= lbR; j++)
        {
         if(osc[i] < osc[i + j])
           {
            isPivotHigh = false;
            break;
           }
        }
      if(isPivotHigh)
         return(i);
     }
   return(-1);
  }

//+------------------------------------------------------------------+
//| Count bars since condition was true                               |
//+------------------------------------------------------------------+
int BarsSinceCondition(const bool &cond[], int fromBar, int maxBars)
  {
   for(int i = fromBar; i < fromBar + maxBars && i < ArraySize(cond); i++)
     {
      if(cond[i])
         return(i - fromBar);
     }
   return(maxBars + 1);
  }

//+------------------------------------------------------------------+
//| Get oscillator value at nth previous pivot found                  |
//+------------------------------------------------------------------+
double ValueWhenPivot(const double &osc[], const int &pivotBars[], int currentBar, int nth, int lbR)
  {
   int count = 0;
   for(int i = currentBar - 1; i >= 0; i--)
     {
      if(pivotBars[i] == 1)
        {
         count++;
         if(count == nth)
            return(osc[i + lbR]);
        }
     }
   return(0.0);
  }

//+------------------------------------------------------------------+
//| Get price value at nth previous pivot found                       |
//+------------------------------------------------------------------+
double ValueWhenPricePivot(const double &price[], const int &pivotBars[], int currentBar, int nth, int lbR)
  {
   int count = 0;
   for(int i = currentBar - 1; i >= 0; i--)
     {
      if(pivotBars[i] == 1)
        {
         count++;
         if(count == nth)
            return(price[i + lbR]);
        }
     }
   return(0.0);
  }

//+------------------------------------------------------------------+
int OnCalculate(const int rates_total,
                const int prev_calculated,
                const datetime &time[],
                const double &open[],
                const double &high[],
                const double &low[],
                const double &close[],
                const long &tick_volume[],
                const long &volume[],
                const int &spread[])
  {
//--- not enough bars
   if(rates_total < InpSlowEMA + InpSignalSMA + InpLbL + InpLbR + 5)
      return(0);

//--- calculate start
   int start;
   if(prev_calculated <= 0)
     {
      start = InpSlowEMA + InpLbL + InpLbR + 5;
      ArrayInitialize(histBuffer, 0.0);
      ArrayInitialize(macdBuffer, EMPTY_VALUE);
      ArrayInitialize(signalBuffer, EMPTY_VALUE);
      ArrayInitialize(bullDivBuffer, EMPTY_VALUE);
      ArrayInitialize(bearDivBuffer, EMPTY_VALUE);
      ArrayInitialize(bullHiddenBuffer, EMPTY_VALUE);
      ArrayInitialize(bearHiddenBuffer, EMPTY_VALUE);
      ArrayInitialize(oscBuffer, 0.0);
     }
   else
      start = prev_calculated - 1;

//--- get MA data
   double fastMA[], slowMA[];
   ArraySetAsSeries(fastMA, false);
   ArraySetAsSeries(slowMA, false);

   if(CopyBuffer(fastMAHandle, 0, 0, rates_total, fastMA) <= 0)
      return(0);
   if(CopyBuffer(slowMAHandle, 0, 0, rates_total, slowMA) <= 0)
      return(0);

//--- calculate MACD and signal
   for(int i = 0; i < rates_total; i++)
     {
      oscBuffer[i] = fastMA[i] - slowMA[i];
     }

//--- calculate signal line using manual EMA/SMA of MACD
   if(InpSignalMAType == MODE_EMA)
     {
      double alpha = 2.0 / (InpSignalSMA + 1.0);
      signalBuffer[0] = oscBuffer[0];
      for(int i = 1; i < rates_total; i++)
         signalBuffer[i] = alpha * oscBuffer[i] + (1.0 - alpha) * signalBuffer[i - 1];
     }
   else
     {
      for(int i = InpSignalSMA - 1; i < rates_total; i++)
        {
         double sum = 0;
         for(int j = 0; j < InpSignalSMA; j++)
            sum += oscBuffer[i - j];
         signalBuffer[i] = sum / InpSignalSMA;
        }
     }

//--- histogram and MACD
   for(int i = 0; i < rates_total; i++)
     {
      macdBuffer[i] = oscBuffer[i];
      histBuffer[i] = oscBuffer[i] - signalBuffer[i];

      //--- histogram color: 0=green grow, 1=green fall, 2=red grow, 3=red fall
      if(i == 0)
         histColorBuffer[i] = histBuffer[i] >= 0 ? 0 : 3;
      else
        {
         if(histBuffer[i] >= 0)
            histColorBuffer[i] = (histBuffer[i - 1] < histBuffer[i]) ? 0 : 1;
         else
            histColorBuffer[i] = (histBuffer[i - 1] < histBuffer[i]) ? 2 : 3;
        }
     }

//--- detect pivots
   int plFound[];
   int phFound[];
   ArrayResize(plFound, rates_total);
   ArrayResize(phFound, rates_total);
   ArrayInitialize(plFound, 0);
   ArrayInitialize(phFound, 0);

   for(int i = InpLbL; i < rates_total - InpLbR; i++)
     {
      if(FindPivotLow(oscBuffer, i, InpLbL, InpLbR, i) == i)
         plFound[i] = 1;
      if(FindPivotHigh(oscBuffer, i, InpLbL, InpLbR, i) == i)
         phFound[i] = 1;
     }

//--- detect divergences
   for(int i = start; i < rates_total; i++)
     {
      bullDivBuffer[i] = EMPTY_VALUE;
      bearDivBuffer[i] = EMPTY_VALUE;
      bullHiddenBuffer[i] = EMPTY_VALUE;
      bearHiddenBuffer[i] = EMPTY_VALUE;

      //--- need enough history for lookback
      if(i - InpLbR < 0 || i - InpLbL - InpLbR - 5 < 0)
         continue;

      int pivotIdx = i - InpLbR;

      //=== REGULAR BULLISH ===
      if(InpPlotBull && plFound[i] == 1)
        {
         //--- find previous pivot low
         int prevPlIdx = -1;
         for(int j = i - 1; j >= 0; j--)
           {
            if(plFound[j] == 1)
              {
               prevPlIdx = j;
               break;
              }
           }

         if(prevPlIdx >= 0)
           {
            //--- Osc: Higher Low
            bool oscHL = oscBuffer[pivotIdx] > oscBuffer[prevPlIdx];
            //--- Price: Lower Low
            bool priceLL = low[pivotIdx] < low[prevPlIdx];
            //--- In range
            int barsSince = i - prevPlIdx;
            bool inRange = (barsSince >= InpRangeLower && barsSince <= InpRangeUpper);
            //--- Below zero
            bool belowZero = true;
            if(InpDontTouchZero)
              {
               double highestOsc = 0;
               for(int k = pivotIdx; k >= MathMax(0, pivotIdx - InpLbL - InpLbR - 5); k--)
                  if(oscBuffer[k] > highestOsc) highestOsc = oscBuffer[k];
               belowZero = (highestOsc < 0);
              }

            if(oscHL && priceLL && inRange && belowZero)
              {
               bullDivBuffer[pivotIdx] = oscBuffer[pivotIdx];
               if(InpDisplayAlert && i >= rates_total - 3 && time[i] != lastAlertTime)
                 {
                  Alert("Regular Bullish divergence on ", Symbol(), " ", EnumToString(Period()));
                  lastAlertTime = time[i];
                 }
              }
           }
        }

      //=== HIDDEN BULLISH ===
      if(InpPlotHiddenBull && plFound[i] == 1)
        {
         int prevPlIdx = -1;
         for(int j = i - 1; j >= 0; j--)
           {
            if(plFound[j] == 1)
              {
               prevPlIdx = j;
               break;
              }
           }

         if(prevPlIdx >= 0)
           {
            bool oscLL = oscBuffer[pivotIdx] < oscBuffer[prevPlIdx];
            bool priceHL = low[pivotIdx] > low[prevPlIdx];
            int barsSince = i - prevPlIdx;
            bool inRange = (barsSince >= InpRangeLower && barsSince <= InpRangeUpper);

            if(oscLL && priceHL && inRange)
              {
               bullHiddenBuffer[pivotIdx] = oscBuffer[pivotIdx];
               if(InpDisplayAlert && i >= rates_total - 3 && time[i] != lastAlertTime)
                 {
                  Alert("Hidden Bullish divergence on ", Symbol(), " ", EnumToString(Period()));
                  lastAlertTime = time[i];
                 }
              }
           }
        }

      //=== REGULAR BEARISH ===
      if(InpPlotBear && phFound[i] == 1)
        {
         int prevPhIdx = -1;
         for(int j = i - 1; j >= 0; j--)
           {
            if(phFound[j] == 1)
              {
               prevPhIdx = j;
               break;
              }
           }

         if(prevPhIdx >= 0)
           {
            //--- Osc: Lower High
            bool oscLH = oscBuffer[pivotIdx] < oscBuffer[prevPhIdx];
            //--- Price: Higher High
            bool priceHH = high[pivotIdx] > high[prevPhIdx];
            //--- In range
            int barsSince = i - prevPhIdx;
            bool inRange = (barsSince >= InpRangeLower && barsSince <= InpRangeUpper);
            //--- Above zero
            bool aboveZero = true;
            if(InpDontTouchZero)
              {
               double lowestOsc = 0;
               for(int k = pivotIdx; k >= MathMax(0, pivotIdx - InpLbL - InpLbR - 5); k--)
                  if(oscBuffer[k] < lowestOsc) lowestOsc = oscBuffer[k];
               aboveZero = (lowestOsc > 0);
              }

            if(oscLH && priceHH && inRange && aboveZero)
              {
               bearDivBuffer[pivotIdx] = oscBuffer[pivotIdx];
               if(InpDisplayAlert && i >= rates_total - 3 && time[i] != lastAlertTime)
                 {
                  Alert("Regular Bearish divergence on ", Symbol(), " ", EnumToString(Period()));
                  lastAlertTime = time[i];
                 }
              }
           }
        }

      //=== HIDDEN BEARISH ===
      if(InpPlotHiddenBear && phFound[i] == 1)
        {
         int prevPhIdx = -1;
         for(int j = i - 1; j >= 0; j--)
           {
            if(phFound[j] == 1)
              {
               prevPhIdx = j;
               break;
              }
           }

         if(prevPhIdx >= 0)
           {
            bool oscHH = oscBuffer[pivotIdx] > oscBuffer[prevPhIdx];
            bool priceLH = high[pivotIdx] < high[prevPhIdx];
            int barsSince = i - prevPhIdx;
            bool inRange = (barsSince >= InpRangeLower && barsSince <= InpRangeUpper);

            if(oscHH && priceLH && inRange)
              {
               bearHiddenBuffer[pivotIdx] = oscBuffer[pivotIdx];
               if(InpDisplayAlert && i >= rates_total - 3 && time[i] != lastAlertTime)
                 {
                  Alert("Hidden Bearish divergence on ", Symbol(), " ", EnumToString(Period()));
                  lastAlertTime = time[i];
                 }
              }
           }
        }
     }

   return(rates_total);
  }
//+------------------------------------------------------------------+
