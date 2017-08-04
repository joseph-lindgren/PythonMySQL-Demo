REPLACE INTO Inventory
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

DELETE FROM Inventory WHERE InStock <= 0
;