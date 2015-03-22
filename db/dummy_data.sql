INSERT INTO question VALUES (0, "I like pie", "I like pi", "I like .py", 2, 1, "Pie");
INSERT INTO question VALUES (1, "I like soccer", "I like cricket", "I like tennis", 1, 1, "Sports");
INSERT INTO question VALUES (2, "I like bananas", "I like apples", "I like pears", 0, 3, "Fruit");
INSERT INTO question VALUES (3, "I like table tennis", "I like videogames", "I like swimming", 1, 3, "All the things");
INSERT INTO question VALUES (4, "I like chocolate", "I like ice-cream", "I like chips", 2, 3, "Food");
INSERT INTO question VALUES (5, "One of these is false", "Two of these are false", "Three of these are false", 1, 2, "Logic");
INSERT INTO question VALUES (6, "I have never visited gabegaming.com", "I made gabegaming.com", "What is gabegaming.com?", 1, 2, "#GabeisMVP");

INSERT INTO vote VALUES (0, 0, 1, NULL);
INSERT INTO vote VALUES (1, 0, 2, NULL);
INSERT INTO vote VALUES (2, 0, 2, NULL);
INSERT INTO vote VALUES (3, 1, 0, NULL);
INSERT INTO vote VALUES (4, 1, 2, NULL);
INSERT INTO vote VALUES (5, 1, 1, NULL);
INSERT INTO vote VALUES (6, 2, 1, NULL);
INSERT INTO vote VALUES (7, 2, 2, NULL);
INSERT INTO vote VALUES (8, 3, 2, NULL);
INSERT INTO vote VALUES (9, 3, 0, NULL);
INSERT INTO vote VALUES (10, 3, 2, NULL);
INSERT INTO vote VALUES (11, 3, 1, NULL);
INSERT INTO vote VALUES (12, 4, 1, NULL);
INSERT INTO vote VALUES (13, 5, 2, NULL);
INSERT INTO vote VALUES (14, 5, 2, NULL);
INSERT INTO vote VALUES (15, 6, 0, NULL);
INSERT INTO vote VALUES (16, 6, 2, NULL);
INSERT INTO vote VALUES (17, 6, 1, NULL);

-- ghetto way of hashing passwords on creation of database
-- refer to database_create for the actual hashing
INSERT INTO user VALUES (NULL, "bruce", HASH("tonotbe"), 0);
INSERT INTO user VALUES (NULL, "alex", HASH("gags"), 0);
INSERT INTO user VALUES (NULL, "deanna", HASH("traitor"), 0);
INSERT INTO user VALUES (NULL, "aaron", HASH("mafiatalk"), 0);
INSERT INTO user VALUES (NULL, "greta", HASH("securecookie"), 0);
