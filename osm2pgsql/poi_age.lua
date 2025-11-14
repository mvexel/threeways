local pois = osm2pgsql.define_table({
    name = 'pois',
    ids = {
        type = 'any', -- https://osm2pgsql.org/doc/manual.html#id-handling
        type_column = 'osm_type',
        id_column = 'osm_id'
    },
    columns = {{
        column = 'name'
    }, {
        column = 'class',
        not_null = true
    }, {
        column = 'category',
        not_null = true
    }, {
        column = 'subclass',
        not_null = true
    }, {
        column = 'geom',
        type = 'point',
        not_null = true,
        projection = 4326
    }, {
        column = 'version',
        type = 'smallint',
        not_null = true
    }, {
        column = 'timestamp',
        sql_type = 'timestamp',
        not_null = true
    }}
})

-- Categories mirror https://wiki.openstreetmap.org/wiki/Map_features#Amenity
local AMENITY_GROUPS = {
    sustenance = {'bar', 'biergarten', 'cafe', 'fast_food', 'food_court', 'ice_cream', 'pub', 'restaurant'},
    education = {'college', 'dancing_school', 'driving_school', 'first_aid_school', 'kindergarten', 'language_school',
                 'library', 'surf_school', 'toy_library', 'research_institute', 'training', 'music_school', 'school',
                 'traffic_park', 'university'},
    transportation = {'bicycle_parking', 'bicycle_repair_station', 'bicycle_rental', 'bicycle_wash', 'boat_rental',
                      'boat_sharing', 'bus_station', 'car_rental', 'car_sharing', 'car_wash', 'compressed_air',
                      'vehicle_inspection', 'charging_station', 'driver_training', 'ferry_terminal', 'fuel', 'grit_bin',
                      'motorcycle_parking', 'parking', 'parking_entrance', 'parking_space', 'taxi', 'weighbridge'},
    financial = {'atm', 'payment_terminal', 'bank', 'bureau_de_change', 'money_transfer', 'payment_centre'},
    healthcare = {'baby_hatch', 'clinic', 'dentist', 'doctors', 'hospital', 'nursing_home', 'pharmacy',
                  'social_facility', 'veterinary'},
    entertainment = {'arts_centre', 'brothel', 'casino', 'cinema', 'community_centre', 'conference_centre',
                     'events_venue', 'exhibition_centre', 'fountain', 'gambling', 'love_hotel', 'music_venue',
                     'nightclub', 'planetarium', 'public_bookcase', 'social_centre', 'stage', 'stripclub', 'studio',
                     'swingerclub', 'theatre'},
    public_service = {'courthouse', 'fire_station', 'police', 'post_box', 'post_depot', 'post_office', 'prison',
                      'ranger_station', 'townhall'},
    facilities = {'bbq', 'bench', 'dog_toilet', 'dressing_room', 'drinking_water', 'give_box', 'mailroom',
                  'parcel_locker', 'shelter', 'shower', 'telephone', 'toilets', 'water_point', 'watering_place'},
    waste = {'sanitary_dump_station', 'recycling', 'waste_basket', 'waste_disposal', 'waste_transfer_station'},
    others = {'animal_boarding', 'animal_breeding', 'animal_shelter', 'animal_training', 'baking_oven', 'clock',
              'crematorium', 'dive_centre', 'funeral_hall', 'grave_yard', 'hunting_stand', 'internet_cafe', 'kitchen',
              'kneipp_water_cure', 'lounger', 'marketplace', 'monastery', 'mortuary', 'photo_booth',
              'place_of_mourning', 'place_of_worship', 'public_bath', 'refugee_site', 'vending_machine'}
}

local AMENITY_LOOKUP = {}
for group, values in pairs(AMENITY_GROUPS) do
    for _, value in ipairs(values) do
        AMENITY_LOOKUP[value] = group
    end
end

local function format_date(ts)
    -- Borrowed from https://github.com/openstreetmap/osm2pgsql/blob/ad541d2a53/flex-config/attributes.lua#L52
    return os.date('!%Y-%m-%dT%H:%M:%SZ', ts)
end

local function process_poi(object)
    local amenity = object.tags.amenity
    if not amenity then
        return nil
    end

    local group = AMENITY_LOOKUP[amenity]
    if not group then
        return nil
    end

    return {
        name = object.tags.name,
        class = 'amenity',
        category = group,
        subclass = amenity,
        version = object.version,
        timestamp = format_date(object.timestamp)
    }
end

function osm2pgsql.process_node(object)
    local record = process_poi(object)
    if record then
        record.geom = object:as_point()
        pois:insert(record)
    end
end

function osm2pgsql.process_way(object)
    if not object.is_closed then
        return
    end

    local record = process_poi(object)
    if record then
        local polygon = object:as_polygon()
        if polygon then
            record.geom = polygon:centroid()
            pois:insert(record)
        end
    end
end
