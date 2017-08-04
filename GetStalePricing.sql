SELECT InStock,typeName,Pricing2.typeID,priceDateTime
FROM (Inventory JOIN Pricing2 ON Inventory.typeID = Pricing2.typeID)
WHERE  TIMESTAMPDIFF(MINUTE,  priceDateTime, NOW() ) > @
GROUP BY typeName;