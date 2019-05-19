#!/usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Frédéric Rodrigo 2012                                      ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
##                                                                       ##
###########################################################################

from .Analyser_Osmosis import Analyser_Osmosis

sql10 = """
SELECT
    nodes.id,
    relation_members.relation_id,
    ST_ASText(geom)
FROM
    {0}nodes AS nodes
    JOIN relation_members ON
        member_id = nodes.id AND
        member_type = 'N' AND
        member_role = ''
WHERE
    nodes.tags - ARRAY['created_by', 'source', 'note:qadastre', 'name'] = ''::hstore
"""

sql11 = """
SELECT
    nodes.id,
    relation_members.relation_id,
    ST_ASText(geom)
FROM
    touched_relations AS relations
    JOIN relation_members ON
        relation_members.relation_id = relations.id AND
        relation_members.member_type = 'N' AND
        relation_members.member_role = ''
    JOIN not_touched_nodes AS nodes ON
        nodes.id = relation_members.member_id AND
        nodes.tags - ARRAY['created_by', 'source', 'note:qadastre', 'name'] = ''::hstore
"""

sql20 = """
SELECT
    ways.id,
    relation_members.relation_id,
    ST_ASText(way_locate(linestring))
FROM
    {0}ways AS ways
    LEFT JOIN relation_members ON
        member_id = ways.id AND
        member_type = 'W'
WHERE
    (member_role IS NULL OR member_role = '') AND
    ways.tags - ARRAY['created_by', 'source', 'note:qadastre', 'name'] = ''::hstore
"""

sql21 = """
SELECT
    ways.id,
    relation_members.relation_id,
    ST_ASText(way_locate(linestring))
FROM
    touched_relations AS relations
    JOIN relation_members ON
        relation_members.relation_id = relations.id AND
        relation_members.member_type = 'W' AND
        relation_members.member_role = ''
    JOIN not_touched_ways AS ways ON
        ways.id = relation_members.member_id AND
        ways.tags - ARRAY['created_by', 'source', 'note:qadastre', 'name'] = ''::hstore
"""

sql30 = """
SELECT
    relations.id,
    relation_members.relation_id,
    ST_AsText(relation_locate(relations.id))
FROM
    {0}relations AS relations
    LEFT JOIN relation_members ON
        member_id = relations.id AND
        member_type = 'R'
WHERE
    (member_role IS NULL OR member_role = '') AND
    relations.tags - ARRAY['created_by', 'source', 'note:qadastre', 'name'] = ''::hstore AND
    relation_locate(relations.id) IS NOT NULL -- We can't locate pure relation or relations
"""

sql31 = """
SELECT
    r.id,
    relation_members.relation_id,
    ST_AsText(relation_locate(r.id))
FROM
    touched_relations AS relations
    JOIN relation_members ON
        relation_members.relation_id = relations.id AND
        relation_members.member_type = 'R' AND
        relation_members.member_role = ''
    JOIN not_touched_relations AS r ON
        r.id = relation_members.member_id AND
        r.tags - ARRAY['created_by', 'source', 'note:qadastre', 'name'] = ''::hstore
"""

class Analyser_Osmosis_Useless(Analyser_Osmosis):

    def __init__(self, config, logger = None):
        Analyser_Osmosis.__init__(self, config, logger)
        self.classs_change[1] = {"item":"1140", "level": 3, "tag": ["fix:chair"], "desc": T_(u"Missing tag or role on node") }
        self.classs_change[2] = {"item":"1140", "level": 3, "tag": ["fix:chair"], "desc": T_(u"Missing tag or role on way") }
        self.classs_change[3] = {"item":"1140", "level": 3, "tag": ["fix:chair"], "desc": T_(u"Missing tag or role on relation") }
        self.callback10 = lambda res: {"class":1, "data":[self.node_full, self.relation_full, self.positionAsText]}
        self.callback20 = lambda res: {"class":2, "data":[self.way_full, self.relation_full if res[1] else None, self.positionAsText]}
        self.callback30 = lambda res: {"class":3, "data":[self.relation_full, self.relation_full if res[1] else None, self.positionAsText]}

    def analyser_osmosis_full(self):
        self.run(sql10.format(""), self.callback10)
        self.run(sql20.format(""), self.callback20)
        self.run(sql30.format(""), self.callback30)

    def analyser_osmosis_diff(self):
        self.run(sql10.format("touched_"), self.callback10)
        self.run(sql11.format(), self.callback10)
        self.run(sql20.format("touched_"), self.callback20)
        self.run(sql21.format(), self.callback20)
        self.run(sql30.format("touched_"), self.callback30)
        self.run(sql31.format(), self.callback30)
