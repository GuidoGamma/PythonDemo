from sqlalchemy import Column, Date, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class DeviceType(Base):
    __table_args__ = {'schema': 'CustomTag'}
    __tablename__ = "DeviceType"

    def __init__(self, Uid, Name):
        self.Uid = Uid
        self.Name = Name

    Uid = Column(String, primary_key=True)
    Name = Column(String)

class CustomTag(Base):
    __table_args__ = {'schema': 'CustomTag'}
    __tablename__ = "CustomTag"

    def __init__(customtag, Uid, DeviceTypeUid, Name, IsFreeText, IsEnum, HasReplacementValue,
                 DefaultValue, AllowedValues, Explanation, ShortDescription, Active):
        customtag.Uid = Uid
        customtag.DeviceTypeUid = DeviceTypeUid
        customtag.Name = Name
        customtag.IsFreeText = IsFreeText
        customtag.IsEnum = IsEnum
        customtag.HasReplacementValue = HasReplacementValue
        customtag.DefaultValue = DefaultValue
        customtag.AllowedValues = AllowedValues
        customtag.Explanation = Explanation
        customtag.ShortDescription = ShortDescription
        customtag.Active = Active

    Uid = Column(String, primary_key=True)
    DeviceTypeUid = Column(String, ForeignKey('CustomTag.DeviceType.Uid'))
    Name = Column(String)
    IsFreeText = Column(Boolean)
    IsEnum = Column(Boolean)
    HasReplacementValue = Column(Boolean)
    DefaultValue = Column(String)
    AllowedValues = Column(String)
    Explanation = Column(String)
    ShortDescription = Column(String)
    Active = Column(Boolean)

    CustomTagDeviceType = relationship("DeviceType")

class Template(Base):
    __table_args__ = {'schema': 'CustomTag'}
    __tablename__ = "Template"

    def __init__(self, Uid, Name, GroupUid, DeviceTypeUid):
        self.Uid = Uid
        self.Name = Name
        self.GroupUid = GroupUid
        self.DeviceTypeUid = DeviceTypeUid

    Uid = Column(String, primary_key=True)
    Name = Column(String)
    GroupUid = Column(String)
    DeviceTypeUid = Column(String, ForeignKey('CustomTag.DeviceType.Uid'))

    TemplateDeviceType = relationship("DeviceType")