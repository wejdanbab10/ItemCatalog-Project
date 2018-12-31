from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import BloodType, Base, Items

engine = create_engine('sqlite:///bloodTypes.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

BloodType1 = BloodType (name = "A+", id = "1", status = "Low Inventory")
session.add(BloodType1)
session.commit()


item1 = Items(name = "A+", description = "Blood type A+ has only the A antigen on red cells (and B antibody in the plasma)", id = "1", amount ="350 ml", blood_type=BloodType1)
session.add(item1)
session.commit()

BloodType2 = BloodType (name = "A-", id = "2", status = "High Inventory")
session.add(BloodType2)
session.commit()


item2 = Items(name = "A-", description = "Blood type A- has only the A antigen on red cells (and B antibody in the plasma)", id = "2", amount ="900 ml", blood_type=BloodType2)
session.add(item2)
session.commit()

BloodType3 = BloodType (name = "B+", id = "3", status = "High Inventory")
session.add(BloodType3)
session.commit()

item3 = Items(name = "B+", description = "Blood type B+ has only the B antigen on red cells (and A antibody in the plasma)", id = "3", amount ="580 ml", blood_type=BloodType3)
session.add(item3)
session.commit()

BloodType4 = BloodType (name = "O+", id = "4", status = "High Inventory")
session.add(BloodType4)
session.commit()


item4 = Items(name = "O+", description = "Blood type O+ has neither A nor B antigens on red cells (but both A and B antibody are in the plasma)", id = "4", amount ="500 ml", blood_type=BloodType4)
session.add(item4)
session.commit()

BloodType5 = BloodType (name = "O-", id = "5", status = "High Inventory")
session.add(BloodType5)
session.commit()

item5 = Items(name = "O-", description = "Blood type O- has neither A nor B antigens on red cells (but both A and B antibody are in the plasma)", id = "5", amount ="650 ml", blood_type=BloodType5)
session.add(item5)
session.commit()

BloodType6 = BloodType (name = "AB+", id = "6", status = "Low Inventory")
session.add(BloodType6)
session.commit()

item6 = Items(name = "AB+", description = "Blood type AB+ has both A and B antigens on red cells (but neither A nor B antibody in the plasma)", id = "6", amount ="450 ml", blood_type=BloodType6)
session.add(item6)
session.commit()

print "All the Blood Bank data are added!"


