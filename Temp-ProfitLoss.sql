DROP TEMPORARY TABLE Profit
;
CREATE TEMPORARY TABLE Profit
SELECT Pricing2.*,InStock,Investment,typeName,cashOut+Investment 
FROM Pricing2 JOIN Inventory 
ON Pricing2.typeID = Inventory.typeID
WHERE cashOut + Investment > 0
ORDER BY Pricing2.typeID
;
DROP TEMPORARY TABLE Loss
;
CREATE TEMPORARY TABLE Loss
SELECT Pricing2.*,InStock,Investment,typeName,cashOut+Investment
FROM Pricing2 JOIN Inventory 
ON Pricing2.typeID = Inventory.typeID
WHERE cashOut + Investment < 0 
ORDER BY TypeName
;
SELECT * FROM Profit
;
SELECT SUM(cashOut+Investment)/1000000 AS MillProfit 
FROM Profit
;
SELECT * FROM Loss
;
SELECT SUM(cashOut+Investment)/1000000 AS MillLoss 
FROM Loss
;

