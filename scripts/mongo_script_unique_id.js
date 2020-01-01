db.annonces.aggregate(
    { $group: { 
        // Group by fields to match on (a,b)
        _id: { 'a' : "$annonce.idannonce" },

        // Count number of matching docs for the group
        count: { $sum:  1 },

        // Save the _id for matching docs
        docs: { $push: "$_id" }
    }},

    // Limit results to duplicates (more than 1 match) 
    { $match: {
        count: { $gt : 1 }
    }}
)
