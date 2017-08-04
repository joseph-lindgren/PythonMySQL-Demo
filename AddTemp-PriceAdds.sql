CREATE TEMPORARY TABLE PriceAdds
SELECT Inventory.typeid AS ToAdd, Pricing2.typeID AS Missing, Inventory.typeName AS Name
FROM Pricing2 RIGHT JOIN Inventory
ON Pricing2.typeID = Inventory.typeid
WHERE Pricing2.typeid IS NULL
;
INSERT INTO Pricing2(typeID)
SELECT ToAdd
FROM PriceAdds
;