/*
 * Extras
 *
 * @date    16.02.2023
 *
 * @author Jasper Hustedt, Timo Lüttig
 * @version 1.0
 *
 * Provides methods used by all Api calls requesting extras
 *
 */
package org.texttechnologylab.timemachines.functions;

import com.mongodb.client.model.Accumulators;
import com.mongodb.client.model.Aggregates;
import com.mongodb.client.model.Projections;
import org.bson.Document;
import org.bson.conversions.Bson;
import org.json.simple.JSONObject;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.texttechnologylab.timemachines.App;
import org.texttechnologylab.timemachines.mongodb.MongoDBConnectionHandler;
import org.texttechnologylab.timemachines.cameo.CameoCodeTranslator;
import spark.Request;
import spark.Response;

import java.util.*;

public class Extras {
    private Extras() {
    }

    private static Logger logger = LoggerFactory.getLogger(Extras.class);

    // nur Event Typen und Akteure abfragen

    /**
     * Method to request events with only their actors field from a server via filters.
     *
     * @param req
     * @param res
     * @return Json structure containing all actors in events with the given filters
     * from req
     */
    public static JSONObject getActors(Request req, Response res) {
        res.type("application/json");
        ArrayList<Document> list = new ArrayList<>();

        Bson filter = Helper.createBsonFilter(req);

        String limit = req.queryParams("limit");
        List<Bson> aggregation = new ArrayList<>();
        if (limit != null)
            aggregation.add(new Document("$limit", Integer.parseInt(limit)));

        aggregation.add(new Document("$match", filter));
        aggregation.add(Aggregates.unwind("$Actors"));
        aggregation.add(Aggregates.group("$Actors.Name",
                Accumulators.sum("Count", 1),
                Accumulators.first("Actor", "$Actors.Name"),
                Accumulators.first("Location", "$Actors.Location"),
                Accumulators.first("Type", "$Actors.Type")));
        aggregation.add(Aggregates.sort(new Document("Count", -1)));
        MongoDBConnectionHandler.getInstance().database.getCollection(App.collection)
                .aggregate(aggregation).into(list);

        logger.info("Events amount: " + list.size());
        JSONObject obj = new JSONObject();
        obj.put("results", list);

        return (obj);
    }

    /**
     * Method to request events with only their type field from a server via filters.
     *
     * @param req
     * @param res
     * @return Json structure containing all types in events with the given filters
     * from req
     */
    public static JSONObject getTypes(Request req, Response res) {
        res.type("application/json");
        ArrayList<Document> list = new ArrayList<>();

        Bson filter = Helper.createBsonFilter(req);

        String limit = req.queryParams("limit");
        List<Bson> aggregation = new ArrayList<>();
        if (limit != null)
            aggregation.add(new Document("$limit", Integer.parseInt(limit)));

        aggregation.add(new Document("$match", filter));


        aggregation.add(Aggregates.group("$Type",
                Accumulators.sum("Count", 1),
                Accumulators.first("Type", "$Type")));

        MongoDBConnectionHandler.getInstance().database.getCollection(App.collection).aggregate(aggregation)
                .into(list);


        System.out.println("Events amount: " + list.size());
        JSONObject obj = new JSONObject();
        obj.put("results", enhanceTypes(list));

        return (obj);
    }

    /**
     * Method to count, group and sort types.
     *
     * @param list containing types
     * @return distinct types from list with count
     * @return
     */
    public static List<Document> enhanceTypes(List<Document> list) {
        ArrayList<Document> groups = new ArrayList<>();
        for (Document doc : list) {
            Document newdoc = new Document();
            newdoc.append("Count", doc.getInteger("Count"));
            String type = doc.getString("Type");

            newdoc.append("Type", doc.getString("Type"));
            if (doc.getString("Type") == null || CameoCodeTranslator.getTypeValue(doc.getString("Type")) == null)
                continue;
            newdoc.append("Type_Name", CameoCodeTranslator.getTypeValue(doc.getString("Type")));

            newdoc.append("BaseType", Helper.getFirstTwoCharsOfString(type));
            newdoc.append("BaseType_Name", CameoCodeTranslator.getTypeValue(Helper.getFirstTwoCharsOfString(type)));
            groups.add(newdoc);
        }
        groups.sort(Comparator.comparing(a -> a.getInteger("Count"), Comparator.reverseOrder()));
        return groups;
    }
}
