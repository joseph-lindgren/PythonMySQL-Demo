SELECT * FROM 
	(SELECT 
		SUM(quantity*
			CASE WHEN transactionType = "sell" THEN -1 
				 ELSE 1 
			END) AS InStock,
		(SUM(-quantity*price*
			CASE WHEN transactionType = "sell" THEN -(1-.025)
				 ELSE (1+.004 )
			END)/
		SUM(quantity*
			CASE WHEN transactionType = "sell" THEN -1 
				 ELSE 1 
			END)) AS InvestmentPerItem,
	typeName, typeID
	FROM Transactions
	GROUP BY typeName
	) AS R
WHERE InStock > 0
ORDER BY typeName;

SELECT SUM(Investment) FROM
	(SELECT * FROM 
		(SELECT 
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
		) AS R
	WHERE InStock > 0 OR typeName = "PLEX"
	) AS S;