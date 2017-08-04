SELECT typeName, typeID, InStock FROM 
	(SELECT typeName AS e , transactionType AS f 
	FROM Transactions
	WHERE transactionType IS NULL) AS A
	RIGHT JOIN
	(SELECT typeName, transactionType, typeID, SUM(quantity*
			CASE WHEN transactionType = "sell" THEN -1 
				 ELSE 1 
			END) as InStock
	FROM Transactions
	GROUP BY typeName) AS B
	ON A.e = B.typeName
WHERE A.e IS NULL;