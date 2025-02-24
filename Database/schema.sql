-- PostGIS extension is required for geolocation data Schema wont work without it
CREATE EXTENSION IF NOT EXISTS postgis;

-- Lookup Tables
CREATE TABLE Gender (
    GenderID SERIAL PRIMARY KEY,
    GenderName VARCHAR(20) UNIQUE
);

-- Core Profile Data
CREATE TABLE Profile (
    ProfileID SERIAL PRIMARY KEY,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    MiddleName VARCHAR(50),
    Email VARCHAR(100) UNIQUE,
    Title VARCHAR(50),
    GenderID INT REFERENCES Gender(GenderID),
    CreatedAt TIMESTAMP DEFAULT NOW(),
    UpdatedAt TIMESTAMP DEFAULT NOW()
);

CREATE TABLE Country (
    CountryCode CHAR(2) PRIMARY KEY,
    CountryName VARCHAR(100) UNIQUE
);

-- Device Management
CREATE TABLE Device (
    DeviceID UUID PRIMARY KEY,
    ProfileID INT REFERENCES Profile(ProfileID),
    DeviceCarrier VARCHAR(100),
    CreatedAt TIMESTAMP DEFAULT NOW(),
    IsActive BOOLEAN DEFAULT TRUE
);

-- Geolocation Data (PostGIS enabled)
CREATE TABLE GeolocationData (
    LocationID BIGSERIAL PRIMARY KEY,
    DeviceID UUID REFERENCES Device(DeviceID),
    ProfileID INT REFERENCES Profile(ProfileID),
    EventTime TIMESTAMP,
    Geography GEOGRAPHY(PointZ, 4326),  -- Stores lat/long/altitude
    HorizontalAccuracy FLOAT,
    VerticalAccuracy FLOAT,
    CountryCode CHAR(2) REFERENCES Country(CountryCode),
    IPAddressV4 INET,
    IPAddressV6 INET,
    CreatedAt TIMESTAMP DEFAULT NOW()
);

-- Address Information
CREATE TABLE Address (
    AddressID SERIAL PRIMARY KEY,
    ProfileID INT REFERENCES Profile(ProfileID),
    AddressLine1 VARCHAR(100),
    AddressLine2 VARCHAR(100),
    City VARCHAR(50),
    State VARCHAR(50),
    ZIP VARCHAR(20),
    IsPrimary BOOLEAN DEFAULT FALSE,
    CreatedAt TIMESTAMP DEFAULT NOW()
);

-- Social Media
CREATE TABLE SocialMedia (
    SocialID SERIAL PRIMARY KEY,
    ProfileID INT REFERENCES Profile(ProfileID),
    Platform VARCHAR(50),
    Handle VARCHAR(100),
    Verified BOOLEAN DEFAULT FALSE,
    CreatedAt TIMESTAMP DEFAULT NOW()
);

-- Relationships
CREATE TABLE RelationshipType (
    RelationshipTypeID SERIAL PRIMARY KEY,
    TypeName VARCHAR(50) UNIQUE
);

CREATE TABLE Relationship (
    RelationshipID SERIAL PRIMARY KEY,
    Profile1ID INT REFERENCES Profile(ProfileID),
    Profile2ID INT REFERENCES Profile(ProfileID),
    RelationshipTypeID INT REFERENCES RelationshipType(RelationshipTypeID),
    StartDate DATE,
    EndDate DATE,
    CreatedAt TIMESTAMP DEFAULT NOW()
);

-- Work Information
CREATE TABLE Employer (
    EmployerID SERIAL PRIMARY KEY,
    EmployerName VARCHAR(100) UNIQUE,
    Industry VARCHAR(50),
    Headquarters VARCHAR(100)
);

CREATE TABLE WorkHistory (
    WorkHistoryID SERIAL PRIMARY KEY,
    ProfileID INT REFERENCES Profile(ProfileID),
    EmployerID INT REFERENCES Employer(EmployerID),
    JobTitle VARCHAR(100),
    StartDate DATE,
    EndDate DATE,
    CreatedAt TIMESTAMP DEFAULT NOW()
);

-- Preferences & Habits
CREATE TABLE FoodPreference (
    PreferenceID SERIAL PRIMARY KEY,
    ProfileID INT REFERENCES Profile(ProfileID),
    PreferenceType VARCHAR(50),
    Details TEXT,
    CreatedAt TIMESTAMP DEFAULT NOW()
);

CREATE TABLE HabitType (
    HabitTypeID SERIAL PRIMARY KEY,
    TypeName VARCHAR(50) UNIQUE
);

CREATE TABLE HabitLog (
    HabitLogID BIGSERIAL PRIMARY KEY,
    ProfileID INT REFERENCES Profile(ProfileID),
    HabitTypeID INT REFERENCES HabitType(HabitTypeID),
    LogDate DATE,
    Duration INTERVAL,
    CreatedAt TIMESTAMP DEFAULT NOW()
);

-- Events & Routines
CREATE TABLE Event (
    EventID SERIAL PRIMARY KEY,
    EventName VARCHAR(100),
    EventDate DATE,
    Location GEOGRAPHY(Point, 4326),
    CreatedAt TIMESTAMP DEFAULT NOW()
);

CREATE TABLE EventParticipation (
    ParticipationID SERIAL PRIMARY KEY,
    ProfileID INT REFERENCES Profile(ProfileID),
    EventID INT REFERENCES Event(EventID),
    Role VARCHAR(50),
    CreatedAt TIMESTAMP DEFAULT NOW()
);

CREATE TABLE RoutineType (
    RoutineTypeID SERIAL PRIMARY KEY,
    TypeName VARCHAR(50) UNIQUE
);

CREATE TABLE Routine (
    RoutineID SERIAL PRIMARY KEY,
    ProfileID INT REFERENCES Profile(ProfileID),
    RoutineTypeID INT REFERENCES RoutineType(RoutineTypeID),
    Schedule JSONB,
    CreatedAt TIMESTAMP DEFAULT NOW(),
    UpdatedAt TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_geolocation_profile ON GeolocationData(ProfileID);
CREATE INDEX idx_geolocation_time ON GeolocationData(EventTime);
CREATE INDEX idx_geolocation_geo ON GeolocationData USING GIST(Geography);
CREATE INDEX idx_relationships ON Relationship(Profile1ID, Profile2ID);