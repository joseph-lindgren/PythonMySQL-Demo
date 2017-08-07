DROP TEMPORARY TABLE TempInventory
;
CREATE TEMPORARY TABLE TempInventory
SELECT 
	SUM(quantity*
		CASE WHEN transactionType = "sell" THEN -1 
			 ELSE 1 
		END) AS InStock,
	SUM(-quantity*price*
		CASE WHEN transactionType = "sell" THEN -(1-.025)
			 ELSE (1+.004 )
		END) AS Investment,
typeName, typeID
FROM Transactions
GROUP BY typeName
;
SELECT * 
FROM TempInventory
WHERE InStock > 0
ORDER BY typeName
;
SELECT SUM(Investment) FROM
TempInventory
WHERE InStock > 0 OR typeName = "PLEX"
;