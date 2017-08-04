SELECT *,cashOut+Investment 
FROM Pricing2 JOIN Inventory 
ON Pricing2.typeID = Inventory.typeID
WHERE cashOut + Investment > 0
ORDER BY Pricing2.typeID
;

SELECT SUM(cashOut+Investment)/1000000 AS MillProfit 
FROM 
	(SELECT cashOut,Investment 
	FROM Pricing2 JOIN Inventory 
	ON Pricing2.typeID = Inventory.typeID
	WHERE cashOut + Investment > 0 
	ORDER BY TypeName)
	AS Temp1
;

SELECT *,cashOut+Investment 
FROM Pricing2 JOIN Inventory 
ON Pricing2.typeID = Inventory.typeID
WHERE cashOut + Investment < 0 
ORDER BY TypeName
;

SELECT SUM(cashOut+Investment)/1000000 AS MillLoss 
FROM
	(SELECT cashOut,Investment 
	FROM Pricing2 JOIN Inventory 
	ON Pricing2.typeID = Inventory.typeID
	WHERE cashOut + Investment < 0 
	ORDER BY TypeName)
	AS Temp2
;
