'''This file contains all the strings functions to format the payload while sending requests
 to the graphql endpoint'''


def risk_assessment_query_string():
  '''Returns the risk assessment query string to be used in the payload for risk assesment
  
  Returns:
  ----------------
  str: The risk assessment query string
  '''

  return '''query VesselsByIMOs($imo: String!) {
  vesselByIMO(imo: $imo) {
    id
    riskAssessment {
      complianceRisk {
        level
      }
      iuuFishingRisk {
        level
      }
      mavSCSRisk {
        level
        riskIndicators {
          name
        }
      }
      smugglingRisk {
        level
        indicators {
          risk
          name
          count
        }
      }
    }
    class
    flag
  }
}'''

def activities_input(includePropertyChanges:bool,limit:int,offset:int,from_date:str,to_date:str,vesselIdOrImo:str,coordinates:list[list]=None)->dict:
  '''27/04 This returns the propely formatted variables to send in the payload for the activities function
  Args:
  ----------------
  includePropertyChanges: bool

  limit: int
      The number of activities to return. The max limit is 500
  offset: int

  from_date: str
      The start date of the time frame formatted as ISO 8601
  to_date: str
      The end date of time frame formatted as ISO 8601
  vesselIdOrImo: str
      The vessel unique ID assingned by windward or the vessel IMO number
  coordinates: list[list]
      The coordinates for the polygon passed as a list conatining each individual lat and logitude as list
  
  Returns:
  ----------------
  dict: The formatted variables to send in the payload for the request to get activities iwthin a polygon and time frame
  '''
  
  
  # an example of the coordinates list
  
  # "polygon": {
  #     "type": "Polygon",
  #     "coordinates": [
  #       [
  #         [
  #           113.258057,
  #           19.823202
  #         ],
  #         [
  #           113.258057,
  #           23.007113
  #         ],
  #         [
  #           120.629883,
  #           23.007113
  #         ],
  #         [
  #           120.629883,
  #           19.823202
  #         ],
  #         [
  #           113.258057,
  #           19.823202
  #         ]
  #       ]
  #     ]
  #   }
  if coordinates: #27/04 if not coordinates are passed then "null" string is returned with the polygon else the coordinates are formatted as a polygon 
    polygon={
        "type": "Polygon",
        "coordinates": [
          coordinates
        ]
      }
  else:
    polygon="null"
  
  return {
  "input": {
    "includePropertyChanges": includePropertyChanges,
    "limit": limit, 
    "offset": offset,
    "timeRange": {
      "from": from_date,
      "to": to_date
    },
    "vesselIdOrImo": vesselIdOrImo,
    "types": [
      {
        "type": "MEETING"
        
      },
      {
        "type": "STANDING"
      },
      {
        "type": "LOW_SPEED_ANCHORED"
      },
      {
        "type": "LOW_SPEED_DRIFTING"
      },
      {
        "type": "LOW_SPEED_MOORED"
      },
      {
        "type": "LOW_SPEED_FISHING"
      },
      {
        "type": "LOW_SPEED_SERVICE"
      },
      {
        "type": "LOW_SPEED_RESEARCH"
      },
      {
        "type": "LOW_SPEED_OFFSHORE_FACILITY"
      },
      {
        "type": "LOW_SPEED_OTHER"
      },
      {
        "type": "MISSING"
      },
      
      {
        "type": "ID_MANIPULATION"
      },
      {
        "type": "PORT_CALL"
      },
      {
        "type": "DARK_ACTIVITY"
      },
      {
        "type": "MMSI_CHANGE"
      },
      {
        "type": "DEVIATION_FROM_PATTERN_FIRST_IN_POLYGON"
      },
      {
        "type": "COURSE_DEVIATION"
      },
      {
        "type": "ACCIDENT"
      },
      {
        "type": "DESTINATION_CHANGE"
      },
      {
        "type": "ETA_CHANGE"
      },
      {
        "type": "BAD_WEATHER"
      }
    ],
    "polygon": polygon, 
  }
}

def activities_query_string()->str:
  '''Returns the activities query string to be used in the payload for activities
  
  Returns:
  ----------------
  str: The activities query string
  '''
  return '''query VesselTimeline($input: VesselTimelineInput!) {
  vesselTimeline(input: $input) {
    nodes {
      ... on Activity {
        duration
        vesselId
        previousPortId
        startDate
        type
        startCoordinate
        endCoordinate
        nextPortId
        extraFields {
          ... on ExtraFields {
            activityType
          }
          ... on DarkActivityExtraFields {
            destinationChange
            draftChange
          }
          
          ... on DestinationChangeActivityExtraFields {
            newDestination
            oldDestination
          }
          ... on ETAChangeActivityExtraFields {
            newEta
            oldEta
          }
          ... on MeetingExtraFields {
            meetingType
          }
        }
      }
    }
    totalCount
  }
}'''