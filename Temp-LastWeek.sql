DROP TEMPORARY TABLE LastWeek
;
CREATE TEMPORARY TABLE LastWeek
SELECT quantity, price, transactionType, typeName, transactionDateTime, typeID
FROM Transactions 
WHERE TIMESTAMPDIFF(DAY, transactionDateTime, NOW() ) < 7
;
DROP TEMPORARY TABLE LastWeekSummary
;
CREATE TEMPORARY TABLE LastWeekSummary
SELECT 
	SUM(quantity) AS Velocity,
	SUM(quantity*
		CASE WHEN transactionType = "sell" THEN -1 
			 ELSE 1 
		END) AS Delta,
	SUM(-quantity*price*
		CASE WHEN transactionType = "sell" THEN -(1-.025)
			 ELSE (1+.004 )
		END) AS Profit,
typeName, typeID
FROM LastWeek
GROUP BY typeName
;