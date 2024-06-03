import instructor
from openai import OpenAI
from typing import List, Dict,Optional, Union
from pydantic import BaseModel, Field
from datetime import date

import os
from dotenv import load_dotenv
load_dotenv()

class Arguments(BaseModel):
    '''This class is used to define the arguments that are required to send in the query request to the endpoint'''
    key: str = Field(..., description="The name of the argument")
    value: Union[str,List[str]] = Field(..., description="The value of the argument")

class Endpoints(BaseModel):
    
    id: int = Field(..., description="A unique identifier for the question")
    query: str = Field(..., description="The question decomposited as much as possible")
    endpoint: str = Field(..., description="The graphql endpoint that is required to fetch data from the ai to answer this specific question")
    arguments: List[Arguments]= Field(..., description="The parameters that are required to send in the query request to the endpoint. The paramter is a dict with the paramter name as the key and the value you make out")
    subquestions: List[int] = Field(
        default_factory=list,
        description="The other endpoints it relies on to get the data from to answer the question. Check each of the arguments of the endpoint to check if it is available if not add a subquestion to get the data from the other point that it can be retrived from",
    )

class QueryPlan(BaseModel):
    root_question: str = Field(..., description="The root question that the user asked")
    plan: List[Endpoints] = Field(
        ..., description="""The plan to answer the root question by querying different endpoints available in the graphql api
        Make sure every information is present and to answer the question and decompose the question properly into each of it's respective endpoints"""
    )
    route: List[str] = Field(..., description="The route that the query plan takes to answer the question eg: [1,2,3,4]")

class Decomposer():
    '''This class is responsible for decomposing the question into subquestions that can be answered by
      the graphql endpoint
      
      Methods:
      ------------
        decompose_question: This method takes in a question and returns a QueryPlan object which contains
        the decomposed question'''
    def __init__(self):
        openai_key = os.getenv("OPENAI_API_KEY")
        self.client = instructor.patch(OpenAI(api_key=openai_key))
    
    def decompose_question(self, question: str) -> QueryPlan:
        '''This method takes in a question and returns a QueryPlan object which contains
        the decomposed question
        
        Parameters:
        ------------
        question: str
            The question that needs to be decomposed into subquestions
            
        Returns:
        ------------
        QueryPlan : the returned structure is as follows
            The decomposed question into subquestions that can be answered by the graphql endpoint
            {'root_question': 'The root question that the user asked',
            'plan': [
                {
                    'id': 1,
                    'query': 'The question decomposited as much as possible',
                    'endpoint': ['The graphql endpoint that is required to fetch data from the ai to answer this specific question'],
                    'arguments': ['The parameters that are required to send in the query request to the endpoint'],
                    'subquestions': [2, 3, 4]
                }
            ]
            }'''
        retrival = self.client.chat.completions.create(
            model="gpt-4o",
            response_model=QueryPlan,
            temperature=0,
            messages= [
                {
                    "role": "system",
                    "content": '''You are a query understanding system capable of decomposing a question into subparamaters required to answer the question.
                    
                    The arguments which are present in different parts of the graphql endpoint i am about to use are as follows: 
                These are the endpoints that are available in graphql
                type Query {
        searchVesselsByIdentifier(identifier: String!, limit: PositiveInt = 20): [SimplifiedVessel]

        """Query - returns information on a single vessel behaviour"""
        vessel(id: ObjectId!): VesselIntelligence

        """Query - returns information on a single vessel by its IMO"""
        vesselByIMO(imo: String!): VesselIntelligence

        """Query - returns information on a multiple vessels by their IMO"""
        vesselsByIMOs(imos:
        Name	Type	Description
        imos	[String!]!	The Integrated Marine Observing System (IMOS) unique ID.): [VesselIntelligence] --provide the imos as a list of strings
        vesselsByMMSI(mmsi: String!): [VesselIntelligence!]!
        portExpectedArrivals(input: PortExpectedArrivalsInput!): PortExpectedArrivalsConnection!
        vesselsInPort(input: 
        Name	Type	Description
        limit	PositiveInt!	The maximal number of records to return.
        offset	NonNegativeInt!	The number of returned records to skip from the beginning of the record list.
        polygonId	ObjectId!	The unique Windward assigned ID of the port polygon.
        timeRange	DateTimeRange	The time range within which the vessels have visited the port.): VesselsInPortConnection!
        departedFromPortVessels(input: DepartedFromPortVesselsInput!): DepartedFromPortVesselsConnection!
        vesselPropertyChanges(input: VesselPropertyChangesInput!): VesselPropertyChangesConnection!

        """
        The API requires selection of a user defined area and selected time range 
        and returns a list of vessels that transmitted in that selected location and selected time
        """
        vesselsInArea(input: 
            Name	Type	Description
            includePropertyChanges	Boolean!	Whether the property changes which occurred within the timeline are included in the returned results.
            limit	PositiveInt!	The maximal number of records to return.
            offset	NonNegativeInt!	The number of returned records to skip from the beginning of the record list.
            polygon	GeoJSONPolygonGeometryScalar	The polygon of the vessels whose behavioral timeline is returned.
            timeRange	ClosedDateTimeRangeInput!	The time range within which the returned behavioral timelines have occurred.):
           VesselsInAreaConnection!
        vesselsCurrentlyInArea(input: VesselsCurrentlyInAreaInput!): VesselsCurrentlyInAreaConnection!
        riskyVesselsInArea(input: RiskyVesselsInAreaInput!): RiskyVesselsInAreaConnection!
        getActivitiesByDatesAndPolygon(type: ActivityTypes!, timeRange: DateTimeRange!, polygonId: ObjectId!): [Activity]
        activitiesInPolygon(input: ActivitiesInPolygonInput!): ActivitiesInPolygonConnection!
        vesselTimeline(input: VesselTimelineInput!): VesselTimelineConnection!
        advancedVesselsSearch(input: AdvancedVesselSearchInput!): SearchResultsOutput
        getAreaPolygonId(input:
        Name	Type	Description
        area    string  The name of the area to search
        areaType    string      The srea type either port or country.): [FeatureObject] --always required when an area is given to know it's unique polugonid
        searchCompaniesByTerm(searchTerm: String!): [Company!]!
        projectVOIs: [VOI]
        voiAuditLogs(input: VOIAuditLogsInput!): VOIAuditLogsConnection!
        complianceServiceReport(imos: [String], timeRange: DateTimeRange, programs: [ComplianceProgram], risks: [Int]): ComplianceServiceReport
        complianceRiskBy(input: ComplianceRiskByInput!): ComplianceRiskByConnection!
        complianceVesselBuildingBlocksBy(input: ComplianceVesselBuildingBlocksByInput!): ComplianceVesselBuildingBlocksByConnection!

        """Query - retrieve a vessel's profile by IMO"""
        readOnlyVesselProfileLink(vesselId: ObjectId, imo: String, startDate: DateTime, endDate: DateTime, sections: [VesselProfileSectionName!]): ReadOnlyVesselProfileLinkResponse

        """Query - retrieve a link to static company profile"""
        readOnlyCompanyProfileLink(companyId: ObjectId!, startDate: DateTime, endDate: DateTime): ReadOnlyCompanyProfileLinkResponse!

        """
        This service requires area coordinates as an input and generates a link with a snapshot of the area and displays the vessels in it
        """
        readOnlyGeoPresenceLink(
            """
            Sample
            
            {
            "type": "Polygon"
            "coordinates": [
                [
                [2.176516056060791, 41.38813490002815],
                [2.1565604209899902, 41.35480230882416],
                [2.1931135654449463, 41.34268079363133],
                [2.222381830215454, 41.388883479485],
                [2.176516056060791, 41.38813490002815]
                ]
            ]
            }
            """
            area: GeoJSONPolygonGeometryScalar!

            """
            Optional text input to appear above the input area snapshot, the default value is “GEOGRAPHICAL PRESENCE REPORT”
            """
            caption: String
        ): ReadOnlyGeoPresenceLinkResponse

        """Query - returns all GeoJSON map elements by shipment."""
        shipmentGeoJSON(id: ObjectId!): GeoJSONFeatureCollectionScalar

        """Query - returns specific shipments by their ID"""
        trackedShipmentsByIds(ids: [ObjectId!]!, readFromPrimary: Boolean): [TrackedShipment]!

        """Query - returns tracked shipments"""
        trackedShipments(
            skip: NonNegativeInt = 0
            offset: NonNegativeInt! = 0

            """Maximum value is 1000 """
            limit: PositiveInt! = 100
            sort: [SortInput!]
            orderBy: [OrderByInput!]
            filterBy: [FilterByInput!]
            groupBy: GroupByInput
            searchTerm: String
            searchTerms: [String]
            useNewExceptions: Boolean
        ): TrackedShipments!

        """Query - returns all supported carriers"""
        carriers(aliases: [SCAC!]): [Carrier!]!
        businessDataMapping(includeDefaultKeys: Boolean): JSONObject
        sharedShipmentLink(trackedShipmentId: ObjectId!): String
        sharedShipmentsLinks(trackedShipmentIds: [ObjectId!]!): [ShareableLink]
        searchVesselsAPI(input: VesselSearchAPIInput!): VesselSearchAPIConnection!
        publicAPIQuota: [PublicAPIQuota!]
        }
                    ''',

                },
                {
                    "role": "user",
                    "content": question,
                },
            ],
        )

        return(retrival)
    
if __name__ == "__main__":
    decomposer = Decomposer()
    question = "What are the risky vessels in the area of the port of Singapore?"
    plan = decomposer.decompose_question(question)
    print(plan)