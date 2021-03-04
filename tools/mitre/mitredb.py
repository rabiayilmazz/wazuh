#!/usr/bin/env python

# Copyright (C) 2015-2021, Wazuh Inc.
# Created by Wazuh, Inc. <info@wazuh.com>.
# This program is a free software; you can redistribute it and/or modify it under the terms of GPLv2
#
# Example:
#
# python mitredb.py -> install mitre.db in /var/ossec/var/db
# python mitredb.py -d /other/directory/mitre.db  -> install mitre.db in other directory
# python mitredb.py -h -> Help

import json
import os
import pwd
import grp
import argparse
import sys
import copy
import const
from datetime import datetime
from sqlalchemy import create_engine, Column, DateTime, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Metadata(Base):
    """
    In this table are stored the metadata of json file
    The information stored:
        version: version of json (PK)
        name: name
        description: description
    """
    __tablename__ = "metadata"

    version = Column(const.VERSION_t, String, primary_key=True)
    name = Column(const.NAME_t, String, nullable=False)
    description = Column(const.DESCRIPTION_t, String, default=None)


class Technique(Base):
    """
    In this table are stored the techniques of json file
    The information stored:
        id: Used to identify the technique (PK)
        name: Name of the technique
        description: Detailed description of the technique
        created_time: Publish date
        modified_time: Last modification date
        mitre_version: Version of MITRE when created
        mitre_detection: Detection information
        network_requirements:Boolean indicationg network requirements
        remote_support: Boolean indicationg remote support
        revoked_by: ID of the technique that revokes this one, NULL otherwise.
        deprecated: Boolean indicating if this technique is deprecated
        subtechnique_of: ID of the parent technique, NULL otherwise
    """
    __tablename__ = "techniques"

    id = Column(const.ID_t, String, primary_key=True)
    name = Column(const.NAME_t, String, nullable=False)
    description = Column(const.DESCRIPTION_t, String, default=None)
    created_time = Column(const.CREATED_t, DateTime, default=None)
    modified_time = Column(const.MODIFIED_t ,DateTime, default=None)
    mitre_version = Column(const.MITRE_VERSION_t, String, default=None)
    mitre_detection = Column(const.MITRE_DETECTION_t, String, default=None)
    network_requirements = Column(const.NETWORK_REQ_t, Boolean, default=False)
    remote_support = Column(const.REMOTE_SUPPORT_t, Boolean, default=False)
    revoked_by = Column(const.REVOKED_BY_t, String, default=None)
    deprecated = Column(const.DEPRECATED_t, Boolean, default=False)
    subtechnique_of = Column(const.SUBTECHNIQUE_OF_t, String, default=None)

    data_sources = relationship(const.DATASOURCE_r, backref=const.TECHNIQUES_r)
    defenses_bypassed = relationship(const.DEFENSEBYPASSES_r, backref=const.TECHNIQUES_r)
    effective_permissions = relationship(const.EFFECTIVEPERMISSON_r, backref=const.TECHNIQUES_r)
    impacts = relationship(const.IMPACT_r, backref=const.TECHNIQUES_r)
    permissions = relationship(const.PERMISSION_r, backref=const.TECHNIQUES_r)
    requirements = relationship(const.SYSTEMREQ_r, backref=const.TECHNIQUES_r)
    contributors = relationship(const.CONTRIBUTORS_r, backref=const.TECHNIQUES_r)
    platforms = relationship(const.PLATFORMS_r, backref=const.TECHNIQUES_r)
    references = relationship(const.REFERENCES_r, backref=const.TECHNIQUES_r)

class DataSource(Base):
    """
    In this table are stored the Sources for each technique identified
    with key x_mitre_data_sources on json file
    The information stored:
        id: Used to identify the technique (FK)
        source: Data source for this technique
    """
    __tablename__ = "data_source"

    id = Column(const.ID_t, String, ForeignKey(const.TECHNIQUE_ID_fk, ondelete='CASCADE'), primary_key=True)
    source = Column(const.SOURCE_t, String, primary_key=True)


class DefenseByPasses(Base):
    """
    In this table are stored the Defenses bypassed for each technique identified
    with key x_mitre_defense_bypassed on json file
    The information stored:
        id: Used to identify the technique (FK)
        defense: Defense bypassed for this technique
    """
    __tablename__ = "defense_bypassed"

    id = Column(const.ID_t, String, ForeignKey(const.TECHNIQUE_ID_fk, ondelete='CASCADE'), primary_key=True)
    defense = Column(const.DEFENSE_t, String, primary_key=True)


class EffectivePermission(Base):
    """
    In this table are stored the Effective permissions for each technique identified
    with key x_mitre_effective_permissions on json file
    The information stored:
        id: Used to identify the technique (FK)
        permission: Effective permission for this technique
    """
    __tablename__ = "effective_permission"

    id = Column(const.ID_t, String, ForeignKey(const.TECHNIQUE_ID_fk, ondelete='CASCADE'), primary_key=True)
    permission = Column(const.PERMISSION_t, String, primary_key=True)


class Impact(Base):
    """
    In this table are stored the Impacts of each technique identified with
    key x_mitre_impact_type on json file
    The information stored:
        id: Used to identify the technique (FK)
        impact: Impact of this technique
    """
    __tablename__ = "impact"

    id = Column(const.ID_t, String, ForeignKey(const.TECHNIQUE_ID_fk, ondelete='CASCADE'), primary_key=True)
    impact = Column(const.IMPACT_t, String, primary_key=True)


class Permission(Base):
    """
    In this table are stored the Permissions for each technique identified
    with key x_mitre_permissions_required on json file
    The information stored:
        id: Used to identify the technique (FK)
        permission: Permission for this technique
    """
    __tablename__ = "permission"

    id = Column(const.ID_t, String, ForeignKey(const.TECHNIQUE_ID_fk, ondelete='CASCADE'), primary_key=True)
    permission = Column(const.PERMISSION_t, String, primary_key=True)


class SystemRequirement(Base):
    """
    In this table are stored the Requirements for each technique identified
    with key x_mitre_system_requirements on json file
    The information stored:
        id: Used to identify the technique (FK)
        requirements: System requirement for this technique
    """
    __tablename__ = "system_requirement"

    id = Column(const.ID_t, String, ForeignKey(const.TECHNIQUE_ID_fk, ondelete='CASCADE'), primary_key=True)
    requirement = Column(const.REQUIREMENT_t, String, primary_key=True)


class Groups(Base):
    """
    In this table are stored the groups of json file
    The information stored:
        id: Used to identify the group (PK)
        name: Name of the group
        description: Detailed description of the group
        created_time: Publish date
        modified_time: Last modification date
        mitre_version: Version of MITRE when created
        revoked_by: ID of the group that revokes this one, NULL otherwise
        deprecated: Boolean indicating if this group is deprecated
    """
    __tablename__ = "groups"

    Id = Column(const.ID_t, String, primary_key=True)
    name = Column(const.NAME_t, String, nullable=False)
    description = Column(const.DESCRIPTION_t, String, default=None)
    created_time = Column(const.CREATED_t, DateTime, default=None)
    modified_time = Column(const.MODIFIED_t, DateTime, default=None)
    mitre_version = Column(const.MITRE_VERSION_t, String, default=None)
    revoked_by = Column(const.REVOKED_BY_t, String, default=None)
    deprecated = Column(const.DEPRECATED_t, Boolean, default=False)

    aliases = relationship(const.ALIASES_r, backref=const.GROUPS_r)
    contributors = relationship(const.CONTRIBUTORS_r, backref=const.GROUPS_r)
    references = relationship(const.REFERENCES_r, backref=const.GROUPS_r)


class Software(Base):
    """
    In this table are stored the software of json file
    The information stored:
        id: Used to identify the software (PK)
        name: Name of the software
        description: Detailed description of the software
        created_time: Publish date
        modified_time: Last modification date
        mitre_version: Version of MITRE when created
        revoked_by: ID of the software that revokes this one, NULL otherwise
        deprecated: Boolean indicating if this software is deprecated
    """
    __tablename__ = "software"

    Id = Column(const.ID_t, String, primary_key=True)
    name = Column(const.NAME_t, String, nullable=False)
    description = Column(const.DESCRIPTION_t, String, default=None)
    created_time = Column(const.CREATED_t, DateTime, default=None)
    modified_time = Column(const.MODIFIED_t, DateTime, default=None)
    mitre_version = Column(const.MITRE_VERSION_t, String, default=None)
    revoked_by = Column(const.REVOKED_BY_t, String, default=None)
    deprecated = Column(const.DEPRECATED_t, Boolean, default=False)

    aliases = relationship(const.ALIASES_r, backref=const.SOFTWARE_r)
    contributors = relationship(const.CONTRIBUTORS_r, backref=const.SOFTWARE_r)
    platforms = relationship(const.PLATFORMS_r, backref=const.SOFTWARE_r)
    references = relationship(const.REFERENCES_r, backref=const.SOFTWARE_r)


class Mitigations(Base):
    """
    In this table are stored the mitigations of json file
    The information stored:
        id: Used to identify the mitigation (PK)
        name: Name of the mitigation
        description: Detailed description of the mitigation
        created_time: Publish date
        modified_time: Last modification date
        mitre_version: Version of MITRE when created
        revoked_by: ID of the mitigation that revokes this one, NULL otherwise
        deprecated: Boolean indicating if this mitigation is deprecated
    """
    __tablename__ = "mitigations"

    Id = Column(const.ID_t, String, primary_key=True)
    name = Column(const.NAME_t, String, nullable=False)
    description = Column(const.DESCRIPTION_t, String, default=None)
    created_time = Column(const.CREATED_t, DateTime, default=None)
    modified_time = Column(const.MODIFIED_t, DateTime, default=None)
    mitre_version = Column(const.MITRE_VERSION_t, String, default=None)
    revoked_by = Column(const.REVOKED_BY_t, String, default=None)
    deprecated = Column(const.DEPRECATED_t, Boolean, default=False)

    references = relationship(const.REFERENCES_r, backref=const.MITIGATIONS_r)


class Aliases(Base):
    """
    In this table are stored the aliases of json file
    The information stored:
        id: Used to identify the technique, mitigation, group or software (FK) (PK)
        alias: Alias related to this item (PK).
    """
    __tablename__ = "aliase"

    Id = Column(const.ID_t, String, primary_key=True)
    alias = Column(const.ALIAS_t, String, nullable=False)

    def __init__(self, Id="", alias="") :
        self.alias = alias

class Contributors(Base):
    """
    In this table are stored the contributors of json file
    The information stored:
        id: Used to identify the technique, mitigation, group or software (FK) (PK).
        contributor: Contributor related to this item (PK).
    """
    __tablename__ = "contributor"

    Id = Column(const.ID_t, String, primary_key=True)
    contributor = Column(const.CONTRIBUTOR_t, String, nullable=False)

    def __init__(self, Id="", contributor="") :
        self.contributor = contributor

class Platforms(Base):
    """
    In this table are stored the platforms of json file
    The information stored:
        id: Used to identify the technique, mitigation, group or software (FK) (PK).
        platform: OS related to this item (PK).
    """
    __tablename__ = "platform"

    Id = Column(const.ID_t, String, primary_key=True)
    platform = Column(const.PLATFORM_t, String, nullable=False)

    def __init__(self, Id="", platform="") :
        self.platform = platform

class References(Base):
    """
    In this table are stored the references of json file
    The information stored:
        id: Used to identify the tactic, technique, mitigation, group or software (FK) (PK).
        source: Source of this reference (PK).
        external_id: ID associated with this item (only in case of source mitre-attack).
        url: URL of the reference.
        description: Description of the reference.
    """
    __tablename__ = "reference"

    Id = Column(const.ID_t, String, primary_key=True)
    source = Column(const.SOURCE_t, String, nullable=False)
    external_id = Column(const.EXTERNAL_ID_t, String, default=None)
    url = Column(const.URL_t, String, default=None)
    description = Column(const.DESCRIPTION_t, String, default=None)

    def __init__(self, Id="", source="", external_id=None, url=None, description=None) :
        self.source = source
        self.external_id = external_id
        self.url = url
        self.description = description



class Tactics(Base):
    """
    In this table are stored the tactics of json file
    The information stored:
        id: Used to identify the tactic (PK)
        name: Name of the tactic
        description: Detailed description of the tactic
        created_time: Publish date
        modified_time: Last modification date
        short_name: Short name of the tactic
    """
    __tablename__ = "tactics"

    Id = Column(const.ID_t, String, primary_key=True)
    name = Column(const.NAME_t, String, nullable=False)
    description = Column(const.DESCRIPTION_t, String, default=None)
    created_time = Column(const.CREATED_t, DateTime, default=None)
    modified_time = Column(const.MODIFIED_t, DateTime, default=None)
    short_name = Column(const.SHORT_NAME_t, String, default=None)

    references = relationship(const.REFERENCES_r, backref=const.TACTICS_r)

class Phases(Base):
    """
    This table stores the relationship between techniques and the tactics table.
    The information stored:
        tactic_id: Used to identify the tactic (FK) (PK)
        tech_id: Used to identify the technique (FK) (PK)
    """
    __tablename__ = "phases"

    tactic_id = Column(const.TACTIC_ID_t, String, ForeignKey(const.TACTICS_ID_fk, ondelete='CASCADE'), primary_key=True)
    tech_id = Column(const.TECH_ID_t, String, ForeignKey(const.TECHNIQUE_ID_fk, ondelete='CASCADE'), primary_key=True)

def parse_table_(function, data_object):
    table = function()
    table.Id = data_object[const.ID_j]
    table.name = data_object[const.NAME_j]

    if const.DESCRIPTION_j in data_object:
        table.description = data_object[const.DESCRIPTION_j]

    if const.CREATED_j in data_object:
        table.created_time = datetime.strptime(data_object[const.CREATED_j], const.TIME_FORMAT)

    if const.MODIFIED_j in data_object:
        table.modified_time = datetime.strptime(data_object[const.MODIFIED_j], const.TIME_FORMAT)

    if function.__name__ == 'Tactics':
        if const.SHORT_NAME_j in data_object:
            table.short_name = data_object[const.SHORT_NAME_j]
    elif function.__name__ == 'Groups' or \
            function.__name__ == 'Software' or \
            function.__name__ == 'Mitigations':
        if const.MITRE_VERSION_j in data_object:
            table.mitre_version = data_object[const.MITRE_VERSION_j]
        if const.DEPRECATED_j in data_object:
            table.deprecated = data_object[const.DEPRECATED_j]

    # Alias
    if data_object.get(const.ALIAS_j):
        for alias in list(set(data_object[const.ALIAS_j])):
            o_alias = Aliases(techniques=technique, alias=alias)
            o_alias.Id = data_object[const.ID_j]
            table.aliases.append(o_alias)
    # Contributor
    if data_object.get(const.CONTRIBUTOR_j):
        for contributor in list(set(data_object[const.CONTRIBUTOR_j])):
            o_contributor = Contributors(techniques=technique, contributor=contributor)
            o_contributor.Id = data_object[const.ID_j]
            table.contributors.append(o_contributor)
    # Platform
    if data_object.get(const.PLATFORM_j):
        for platform in list(set(data_object[const.PLATFORM_j])):
            o_platform = Platforms(techniques=technique, platform=platform)
            o_platform.Id = data_object[const.ID_j]
            table.platforms.append(o_platform)
    # External References
    if data_object.get(const.EXTERNAL_REFERENCES_j):
        for ext_reference in list(set(data_object[const.EXTERNAL_REFERENCES_j])):
            o_reference = References(techniques=technique, references=references)
            o_reference.Id = data_object[const.ID_j]
            table.references.append(o_reference)

    return table


def parse_json_techniques(technique_json, phases_table):

    technique = Technique()
    technique.id = technique_json[const.ID_t]
    technique.name = technique_json[const.NAME_t]

    if technique_json.get(const.DESCRIPTION_t):
        technique.description = technique_json[const.DESCRIPTION_t]
    if technique_json.get(const.CREATED_j):
        technique.created_time = datetime.strptime(technique_json[const.CREATED_j], const.TIME_FORMAT)
    if technique_json.get(const.MODIFIED_j):
        technique.modified_time = datetime.strptime(technique_json[const.MODIFIED_j], const.TIME_FORMAT)
    if technique_json.get(const.MITRE_VERSION_j):
        technique.mitre_version = technique_json[const.MITRE_VERSION_j]
    if technique_json.get(const.MITRE_DETECTION_j):
        technique.mitre_detection = technique_json[const.MITRE_DETECTION_j]
    if technique_json.get(const.MITRE_NETWOR_REQ_j):
        technique.network_requirements = technique_json[const.MITRE_NETWOR_REQ_j]
    if technique_json.get(const.MITRE_REMOTE_SUPP_j):
        technique.remote_support = technique_json[const.MITRE_REMOTE_SUPP_j]
    if technique_json.get(const.DEPRECATED_j):
        technique.deprecated = technique_json[const.DEPRECATED_j]
    if technique_json.get(const.DATASOURCE_j):
        for data_source in list(set(technique_json[const.DATASOURCE_j])):
            technique.data_sources.append(DataSource(techniques=technique, source=data_source))
    if technique_json.get(const.DEFENSE_BYPASSED_j):
        for defense in list(set(technique_json[const.DEFENSE_BYPASSED_j])):
            technique.defenses_bypassed.append(DefenseByPasses(techniques=technique, defense=defense))
    if technique_json.get(const.EFFECTIVE_PERMISSION_j):
        for permission in list(set(technique_json[const.EFFECTIVE_PERMISSION_j])):
            technique.effective_permissions.append(EffectivePermission(techniques=technique, permission=permission))
    if technique_json.get(const.IMPACT_TYPE_j):
        for impact in list(set(technique_json[const.IMPACT_TYPE_j])):
            technique.impacts.append(Impact(techniques=technique, impact=impact))
    if technique_json.get(const.PERMISSIONS_REQ_j):
        for permission in list(set(technique_json[const.PERMISSIONS_REQ_j])):
            technique.permissions.append(Permission(techniques=technique, permission=permission))
    if technique_json.get(const.SYSTEM_REQ_j):
        for requirement in list(set(technique_json[const.SYSTEM_REQ_j])):
            technique.requirements.append(SystemRequirement(techniques=technique, requirement=requirement))
    if technique_json.get(const.PHASES_j):
        for phase in technique_json[const.PHASES_j]:
             phases_table.append([technique.id, phase[const.PHASE_NAME_j]])
    # Contributor
    if technique_json.get(const.CONTRIBUTOR_j):
        for contributor in list(set(technique_json[const.CONTRIBUTOR_j])):
            o_contributor = Contributors(techniques=technique, contributor=contributor)
            o_contributor.id = technique_json[const.ID_t]
            technique.contributors.append(o_contributor)
    # Platform
    if technique_json.get(const.PLATFORM_j):
        for platform in list(set(technique_json[const.PLATFORM_j])):
            o_platform = Platforms(techniques=technique, platform=platform)
            o_platform.id = technique_json[const.ID_t]
            technique.platforms.append(o_platform)
    # External References
    if technique_json.get(const.EXTERNAL_REFERENCES_j):
        for ext_reference in list(set(technique_json[const.EXTERNAL_REFERENCES_j])):
            o_reference = References(techniques=technique, references=references)
            o_reference.id = technique_json[const.ID_t]
            technique.references.append(o_reference)

    return technique


def parse_json_relationships(relationships_json, session):
    if relationships_json.get(const.RELATIONSHIP_TYPE_j) == const.REVOKED_BY_j:
        if relationships_json[const.SOURCE_REF_j].startswith(const.INTRUSION_SET_j):
            groups = session.query(Groups).get(relationships_json[const.SOURCE_REF_j])
            groups.revoked_by = relationships_json[const.TARGET_REF_j]

        elif relationships_json[const.SOURCE_REF_j].startswith(const.COURSE_OF_ACTION_j):
            mitigations = session.query(Mitigations).get(relationships_json[const.SOURCE_REF_j])
            mitigations.revoked_by = relationships_json[const.TARGET_REF_j]

        elif relationships_json[const.SOURCE_REF_j].startswith(const.MALWARE_j) or \
                relationships_json[const.SOURCE_REF_j].startswith(const.TOOL_j):
            software = session.query(Software).get(relationships_json[const.SOURCE_REF_j])
            software.revoked_by = relationships_json[const.TARGET_REF_j]

        elif relationships_json[const.SOURCE_REF_j].startswith(const.ATTACK_PATTERN_j):
            technique = session.query(Technique).get(relationships_json[const.SOURCE_REF_j])
            technique.revoked_by = relationships_json[const.TARGET_REF_j]

    elif relationships_json.get(const.RELATIONSHIP_TYPE_j) == const.SUBTECHNIQUE_OF_j:
        technique = session.query(Technique).get(relationships_json[const.SOURCE_REF_j])
        technique.subtechnique_of = relationships_json[const.TARGET_REF_j]

    session.commit()


def parse_list_phases(session, phase_list):
    phase = Phases()

    phase.tech_id = phase_list[0]
    account = session.query(Tactics).filter_by(short_name=phase_list[1]).first()
    phase.tactic_id = account.Id

    # External References
    if session.get(const.EXTERNAL_REFERENCES_j):
        for ext_reference in list(set(session[const.EXTERNAL_REFERENCES_j])):
            o_reference = References(techniques=technique, references=references)
            o_reference.id = phase_list[0]
            phase.references.append(o_reference)

    return phase


def parse_json(pathfile, session, database):
    """
    Parse enterprise-attack.json and fill mitre.db's tables.

    :param pathfile: Path directory where enterprise-attack.json file is
    :param session: SQLAlchemy session
    :param database: path to mitre.db
    :return:
    """
    try:
        phases_table = []
        metadata = Metadata()
        with open(pathfile) as json_file:
            datajson = json.load(json_file)
            metadata.version = datajson[const.VERSION_j]
            for data_object in datajson[const.OBJECT_j]:
                if data_object[const.TYPE_j] == const.IDENTITY_j:
                    metadata.name = data_object[const.NAME_j]
                elif data_object[const.TYPE_j] == const.MARKING_DEFINITION_j:
                    metadata.description = data_object[const.DEFINITION_j][const.STATEMENT_j]
                elif data_object[const.TYPE_j] == const.INTRUSION_SET_j:
                    groups = parse_table_(Groups, data_object)
                    session.add(groups)
                elif data_object[const.TYPE_j] == const.COURSE_OF_ACTION_j:
                    mitigations = parse_table_(Mitigations, data_object)
                    session.add(mitigations)
                elif data_object[const.TYPE_j] == const.MALWARE_j or \
                        data_object[const.TYPE_j] == const.TOOL_j:
                    software = parse_table_(Software, data_object)
                    session.add(software)
                elif data_object[const.TYPE_j] == const.TACTIC_j:
                    tactics = parse_table_(Tactics, data_object)
                    session.add(tactics)
                elif data_object[const.TYPE_j] == const.ATTACK_PATTERN_j:
                    technique = parse_json_techniques(data_object, phases_table)
                    session.add(technique)
                else:
                    continue
                session.commit()

        for table in phases_table:
            phases = parse_list_phases(session, table)
            session.add(phases)

        session.commit()

        with open(pathfile) as json_file:
            datajson = json.load(json_file)
            for data_object in datajson[const.OBJECT_j]:
                if data_object[const.TYPE_j] == const.RELATIONSHIP_j:
                    parse_json_relationships(data_object, session)

        session.add(metadata)
        session.commit()

    except TypeError as t_e:
        print(t_e)
        print("Deleting " + database)
        os.remove(database)
        sys.exit(1)
    except KeyError as k_e:
        print(k_e)
        print("Deleting " + database)
        os.remove(database)
        sys.exit(1)
    except NameError as n_e:
        print(n_e)
        print("Deleting " + database)
        os.remove(database)
        sys.exit(1)


def find(name, path):
    for root, dirs, files in os.walk(path):
        if name in files:
            return os.path.join(root, name)


def main(database=None):
    """
    Main function that creates the mitre database in a chosen directory. It deletes, creates and fills the mitre tables.

    :param database: Directory where mitre.db is. Default: /var/ossec/var/db/mitre.db
    :return:
    """
    if database is None:
        database = "/var/ossec/var/db/mitre.db"
    else:
        if not os.path.isdir('/'.join((str(database).split('/')[0:-1]))):
            raise Exception('Error: Directory not found.')

    pathfile = find('enterprise-attack.json', '../..')

    engine = create_engine('sqlite:///' + database, echo=False)

    # Create a database connection
    Session = sessionmaker(bind=engine)
    session = Session()

    # Delete and create tables
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # Parse enterprise-attack.json file:
    parse_json(pathfile, session, database)

    # User and group permissions
    os.chmod(database, 0o660)
    uid = pwd.getpwnam("root").pw_uid
    gid = grp.getgrnam("ossec").gr_gid
    os.chown(database, uid, gid)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='This script installs mitre.db in a directory.')
    parser.add_argument('--database', '-d', help='-d /your/directory/mitre.db (default: /var/ossec/var/db/mitre.db')
    args = parser.parse_args()
    main(args.database)
