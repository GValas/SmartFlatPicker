// select idannonce, count(idannonce) as count from annonces group by idannonce having count > 1
db.annonces.aggregate([
    {"$group" : {_id: "$annonce.idannonce", count:{$sum:1}}},
    {"$match":  { count: { $gt: 1 } } }
])


// select idannonce, count(idannonce) as count from annonces group by idannonce having count > 1
db.annonces.aggregate([
    {"$group" : {_id: "$annonce.cp", count:{$sum:1}}} ,	
    {"$orderby":{ "_id": -1 }
]).sort( { count: -1 } )
