//+------------------------------------------------------------------+
//|                                        MACD_Divergence_EA.mq5    |
//|                                        MACD Divergence Strategy   |
//+------------------------------------------------------------------+
#property copyright "MACD Divergence Strategy EA"
#property version   "1.00"
#property description "Expert Advisor based on MACD divergence detection"

#include <Trade\Trade.mqh>

input string s1="-----------------------------------------------";
input string s2="----------- MACD Settings ----------------------";
input int    fastEMA                 = 12;
input int    slowEMA                 = 26;
input int    signalSMA               = 9;
input string s3="-----------------------------------------------";
input string s4="----------- Trade Settings ---------------------";
input bool   useClassicalDiv        = true;
input bool   useReverseDiv          = true;
input double riskPercent            = 2.0;
input double riskRewardRatio        = 2.0;
input double slMultiplier           = 1.0;
input int    slLookback             = 5;
input int    maxPositions           = 1;
input int    magicNumber            = 123456;
input string s5="-----------------------------------------------";
input string s6="----------- Exit Settings ----------------------";
input bool   exitOnOppositeSignal   = true;
input bool   useTrailingStop        = false;
input double trailingStopPips       = 50.0;

CTrade trade;

int    macdHandle = INVALID_HANDLE;
double macdBuffer[];
double signalBuffer[];

datetime lastAlertTime = 0;

int OnInit()
{
   macdHandle = iMACD(NULL, 0, fastEMA, slowEMA, signalSMA, PRICE_CLOSE);
   if(macdHandle == INVALID_HANDLE)
   {
      Print("Failed to create MACD handle: ", GetLastError());
      return(INIT_FAILED);
   }

   ArraySetAsSeries(macdBuffer, true);
   ArraySetAsSeries(signalBuffer, true);

   trade.SetExpertMagicNumber(magicNumber);
   trade.SetDeviationInPoints(10);
   trade.SetTypeFilling(ORDER_FILLING_FOK);

   return(INIT_SUCCEEDED);
}

void OnDeinit(const int reason)
{
   if(macdHandle != INVALID_HANDLE)
      IndicatorRelease(macdHandle);
}

void OnTick()
{
   int counted = BarsCalculated(macdHandle);
   if(counted < 0)
      return;

   int copied = CopyBuffer(macdHandle, 0, 0, 100, macdBuffer);
   if(copied <= 0) return;

   copied = CopyBuffer(macdHandle, 1, 0, 100, signalBuffer);
   if(copied <= 0) return;

   double high[], low[];
   ArraySetAsSeries(high, true);
   ArraySetAsSeries(low, true);

   if(CopyHigh(NULL, 0, 0, 100, high) <= 0) return;
   if(CopyLow(NULL, 0, 0, 100, low) <= 0) return;

   datetime time[];
   ArraySetAsSeries(time, true);
   if(CopyTime(NULL, 0, 0, 100, time) <= 0) return;

   double close[];
   ArraySetAsSeries(close, true);
   if(CopyClose(NULL, 0, 0, 100, close) <= 0) return;

   int currentBar = 2;

   int bullSignal = CheckBullishDivergence(currentBar, macdBuffer, signalBuffer, high, low);
   int bearSignal = CheckBearishDivergence(currentBar, macdBuffer, signalBuffer, high, low);

   bool hasBullDiv = (bullSignal > 0 && useClassicalDiv) || (bullSignal < 0 && useReverseDiv);
   bool hasBearDiv = (bearSignal > 0 && useClassicalDiv) || (bearSignal < 0 && useReverseDiv);

   int openPositions = CountPositions();

   if(openPositions > 0 && exitOnOppositeSignal)
   {
      if(CheckCloseOnOpposite(hasBullDiv, hasBearDiv))
         return;
   }

   if(useTrailingStop)
      ManageTrailingStop();

   if(openPositions < maxPositions)
   {
      if(hasBullDiv)
         OpenBuy();

      if(hasBearDiv)
         OpenSell();
   }
}

int CheckBullishDivergence(int shift, double &macd[], double &sig[], double &high[], double &low[])
{
   if(shift < 2 || shift >= ArraySize(macd) - 1)
      return 0;

   if(macd[shift] <= macd[shift-1] &&
      macd[shift] < macd[shift-2] &&
      macd[shift] < macd[shift+1])
   {
      int currentExtremum = shift;
      int lastExtremum = GetIndicatorLastTrough(shift, macd, sig);

      if(lastExtremum > 0)
      {
         if(macd[currentExtremum] > macd[lastExtremum] &&
            low[currentExtremum] < low[lastExtremum])
         {
            return 1;
         }
         if(macd[currentExtremum] < macd[lastExtremum] &&
            low[currentExtremum] > low[lastExtremum])
         {
            return -1;
         }
      }
   }
   return 0;
}

int CheckBearishDivergence(int shift, double &macd[], double &sig[], double &high[], double &low[])
{
   if(shift < 2 || shift >= ArraySize(macd) - 1)
      return 0;

   if(macd[shift] >= macd[shift-1] &&
      macd[shift] > macd[shift-2] &&
      macd[shift] > macd[shift+1])
   {
      int currentExtremum = shift;
      int lastExtremum = GetIndicatorLastPeak(shift, macd, sig);

      if(lastExtremum > 0)
      {
         if(macd[currentExtremum] < macd[lastExtremum] &&
            high[currentExtremum] > high[lastExtremum])
         {
            return 1;
         }
         if(macd[currentExtremum] > macd[lastExtremum] &&
            high[currentExtremum] < high[lastExtremum])
         {
            return -1;
         }
      }
   }
   return 0;
}

int GetIndicatorLastTrough(int shift, double &macd[], double &sig[])
{
   int size = ArraySize(sig);
   for(int i = shift - 5; i >= 2; i--)
   {
      if(i + 2 >= size) continue;
      if(sig[i] <= sig[i-1] && sig[i] <= sig[i-2] &&
         sig[i] <= sig[i+1] && sig[i] <= sig[i+2])
      {
         for(int j = i; j >= 2; j--)
         {
            if(macd[j] <= macd[j-1] && macd[j] < macd[j-2] &&
               macd[j] <= macd[j+1] && macd[j] < macd[j+2])
               return j;
         }
      }
   }
   return 0;
}

int GetIndicatorLastPeak(int shift, double &macd[], double &sig[])
{
   int size = ArraySize(sig);
   for(int i = shift - 5; i >= 2; i--)
   {
      if(i + 2 >= size) continue;
      if(sig[i] >= sig[i-1] && sig[i] >= sig[i-2] &&
         sig[i] >= sig[i+1] && sig[i] >= sig[i+2])
      {
         for(int j = i; j >= 2; j--)
         {
            if(macd[j] >= macd[j-1] && macd[j] > macd[j-2] &&
               macd[j] >= macd[j+1] && macd[j] > macd[j+2])
               return j;
         }
      }
   }
   return 0;
}

int CountPositions()
{
   int count = 0;
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket > 0)
      {
         if(PositionGetString(POSITION_SYMBOL) == Symbol() &&
            PositionGetInteger(POSITION_MAGIC) == magicNumber)
            count++;
      }
   }
   return count;
}

bool CheckCloseOnOpposite(bool hasBullDiv, bool hasBearDiv)
{
   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;

      if(PositionGetString(POSITION_SYMBOL) != Symbol() ||
         PositionGetInteger(POSITION_MAGIC) != magicNumber)
         continue;

      long posType = PositionGetInteger(POSITION_TYPE);

      if(posType == POSITION_TYPE_BUY && hasBearDiv)
      {
         trade.PositionClose(ticket);
         Print("Closed BUY due to bearish divergence signal");
         return true;
      }
      if(posType == POSITION_TYPE_SELL && hasBullDiv)
      {
         trade.PositionClose(ticket);
         Print("Closed SELL due to bullish divergence signal");
         return true;
      }
   }
   return false;
}

void OpenBuy()
{
   double ask = SymbolInfoDouble(Symbol(), SYMBOL_ASK);
   double point = SymbolInfoDouble(Symbol(), SYMBOL_POINT);

   double low[];
   ArraySetAsSeries(low, true);
   if(CopyLow(NULL, 0, 0, slLookback + 5, low) <= 0) return;

   double swingLow = low[ArrayMinimum(low, 0, slLookback + 3)];
   double sl = swingLow - 10 * point;

   double risk = ask - sl;
   if(risk <= 0) return;

   double tp = ask + risk * riskRewardRatio;

   double accountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   double riskAmount = accountBalance * riskPercent / 100.0;
   double tickSize = SymbolInfoDouble(Symbol(), SYMBOL_TRADE_TICK_SIZE);
   double tickValue = SymbolInfoDouble(Symbol(), SYMBOL_TRADE_TICK_VALUE);
   if(tickSize <= 0 || tickValue <= 0) return;

   double slDistance = ask - sl;
   double lotStep = SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_STEP);
   double minLot = SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_MAX);

   double lots = NormalizeDouble(riskAmount / (slDistance / tickSize * tickValue), 2);
   lots = MathMax(lots, minLot);
   lots = MathMin(lots, maxLot);
   lots = MathFloor(lots / lotStep) * lotStep;

   sl = NormalizeDouble(sl, _Digits);
   tp = NormalizeDouble(tp, _Digits);

   if(trade.Buy(lots, Symbol(), ask, sl, tp, "MACD Bull Div"))
      Print("BUY opened: Lots=", lots, " SL=", sl, " TP=", tp);
   else
      Print("BUY failed: ", trade.ResultRetcode(), " - ", trade.ResultRetcodeDescription());
}

void OpenSell()
{
   double bid = SymbolInfoDouble(Symbol(), SYMBOL_BID);
   double point = SymbolInfoDouble(Symbol(), SYMBOL_POINT);

   double high[];
   ArraySetAsSeries(high, true);
   if(CopyHigh(NULL, 0, 0, slLookback + 5, high) <= 0) return;

   double swingHigh = high[ArrayMaximum(high, 0, slLookback + 3)];
   double sl = swingHigh + 10 * point;

   double risk = sl - bid;
   if(risk <= 0) return;

   double tp = bid - risk * riskRewardRatio;

   double accountBalance = AccountInfoDouble(ACCOUNT_BALANCE);
   double riskAmount = accountBalance * riskPercent / 100.0;
   double tickSize = SymbolInfoDouble(Symbol(), SYMBOL_TRADE_TICK_SIZE);
   double tickValue = SymbolInfoDouble(Symbol(), SYMBOL_TRADE_TICK_VALUE);
   if(tickSize <= 0 || tickValue <= 0) return;

   double slDistance = sl - bid;
   double lotStep = SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_STEP);
   double minLot = SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_MIN);
   double maxLot = SymbolInfoDouble(Symbol(), SYMBOL_VOLUME_MAX);

   double lots = NormalizeDouble(riskAmount / (slDistance / tickSize * tickValue), 2);
   lots = MathMax(lots, minLot);
   lots = MathMin(lots, maxLot);
   lots = MathFloor(lots / lotStep) * lotStep;

   sl = NormalizeDouble(sl, _Digits);
   tp = NormalizeDouble(tp, _Digits);

   if(trade.Sell(lots, Symbol(), bid, sl, tp, "MACD Bear Div"))
      Print("SELL opened: Lots=", lots, " SL=", sl, " TP=", tp);
   else
      Print("SELL failed: ", trade.ResultRetcode(), " - ", trade.ResultRetcodeDescription());
}

void ManageTrailingStop()
{
   double point = SymbolInfoDouble(Symbol(), SYMBOL_POINT);
   double trailDistance = trailingStopPips * 10 * point;

   for(int i = PositionsTotal() - 1; i >= 0; i--)
   {
      ulong ticket = PositionGetTicket(i);
      if(ticket == 0) continue;

      if(PositionGetString(POSITION_SYMBOL) != Symbol() ||
         PositionGetInteger(POSITION_MAGIC) != magicNumber)
         continue;

      long posType = PositionGetInteger(POSITION_TYPE);
      double openPrice = PositionGetDouble(POSITION_PRICE_OPEN);
      double currentSL = PositionGetDouble(POSITION_SL);
      double currentTP = PositionGetDouble(POSITION_TP);

      if(posType == POSITION_TYPE_BUY)
      {
         double bid = SymbolInfoDouble(Symbol(), SYMBOL_BID);
         double newSL = NormalizeDouble(bid - trailDistance, _Digits);
         if(newSL > currentSL + point && newSL < bid)
         {
            trade.PositionModify(ticket, newSL, currentTP);
         }
      }
      else if(posType == POSITION_TYPE_SELL)
      {
         double ask = SymbolInfoDouble(Symbol(), SYMBOL_ASK);
         double newSL = NormalizeDouble(ask + trailDistance, _Digits);
         if(newSL < currentSL - point && newSL > ask)
         {
            trade.PositionModify(ticket, newSL, currentTP);
         }
      }
   }
}
