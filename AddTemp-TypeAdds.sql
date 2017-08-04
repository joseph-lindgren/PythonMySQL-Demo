CREATE TEMPORARY TABLE TypeAdds
SELECT typeids.typeid AS Missing, Transactions.typeID AS ToAdd, Transactions.typeName AS Name
FROM typeids RIGHT JOIN Transactions 
ON typeids.typeid = Transactions.typeID 
WHERE typeids.typeid IS NULL
GROUP BY Transactions.typeID
;
INSERT INTO typeids
SELECT ToAdd, Name, 1 FROM TypeAdds
;