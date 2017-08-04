SELECT quantity, price, transactionType, typeName, transactionDateTime
FROM Transactions 
WHERE TIMESTAMPDIFF(HOUR, transactionDateTime, NOW() ) < 24
ORDER BY transactionDateTime;

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
		SUM(quantity)
		) AS InvestmentPerItem,
	typeName, typeID
	FROM Transactions
	WHERE TIMESTAMPDIFF(HOUR, transactionDateTime, NOW() ) < 24
	GROUP BY typeName
	) AS R
ORDER BY typeName;