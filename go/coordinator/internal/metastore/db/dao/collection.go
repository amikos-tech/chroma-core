package dao

import (
	"database/sql"

	"go.uber.org/zap"
	"gorm.io/gorm"

	"github.com/chroma/chroma-coordinator/internal/common"
	"github.com/chroma/chroma-coordinator/internal/metastore/db/dbmodel"
	"github.com/go-sql-driver/mysql"
	"github.com/pingcap/log"
)

type collectionDb struct {
	db *gorm.DB
}

var _ dbmodel.ICollectionDb = &collectionDb{}

func (s *collectionDb) DeleteAll() error {
	return s.db.Where("1 = 1").Delete(&dbmodel.Collection{}).Error
}

func (s *collectionDb) GetCollections(id *string, name *string, topic *string) ([]*dbmodel.CollectionAndMetadata, error) {
	var collections []*dbmodel.CollectionAndMetadata

	query := s.db.Table("collections").
		Select("collections.id, collections.name, collections.topic, collections.dimension, collection_metadata.key, collection_metadata.str_value, collection_metadata.int_value, collection_metadata.float_value").
		Joins("LEFT JOIN collection_metadata ON collections.id = collection_metadata.collection_id").
		Order("collections.id")

	if id != nil {
		query = query.Where("collections.id = ?", *id)
	}
	if topic != nil {
		query = query.Where("collections.topic = ?", *topic)
	}
	if name != nil {
		query = query.Where("collections.name = ?", *name)
	}

	rows, err := query.Rows()
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var currentCollectionID string = ""
	var metadata []*dbmodel.CollectionMetadata
	var currentCollection *dbmodel.CollectionAndMetadata

	for rows.Next() {
		var (
			collectionID        string
			collectionName      string
			collectionTopic     string
			collectionDimension sql.NullInt32
			key                 sql.NullString
			strValue            sql.NullString
			intValue            sql.NullInt64
			floatValue          sql.NullFloat64
		)

		err := rows.Scan(&collectionID, &collectionName, &collectionTopic, &collectionDimension, &key, &strValue, &intValue, &floatValue)
		if err != nil {
			log.Error("scan collection failed", zap.Error(err))
			return nil, err
		}
		if collectionID != currentCollectionID {
			currentCollectionID = collectionID
			metadata = nil

			currentCollection = &dbmodel.CollectionAndMetadata{
				Collection: &dbmodel.Collection{
					ID:    collectionID,
					Name:  &collectionName,
					Topic: &collectionTopic,
				},
				CollectionMetadata: metadata,
			}
			if collectionDimension.Valid {
				currentCollection.Collection.Dimension = &collectionDimension.Int32
			} else {
				currentCollection.Collection.Dimension = nil
			}

			if currentCollectionID != "" {
				collections = append(collections, currentCollection)
			}
		}

		collectionMetadata := &dbmodel.CollectionMetadata{
			CollectionID: collectionID,
		}

		if key.Valid {
			collectionMetadata.Key = &key.String
		} else {
			collectionMetadata.Key = nil
		}

		if strValue.Valid {
			collectionMetadata.StrValue = &strValue.String
		} else {
			collectionMetadata.StrValue = nil
		}
		if intValue.Valid {
			collectionMetadata.IntValue = &intValue.Int64
		} else {
			collectionMetadata.IntValue = nil
		}
		if floatValue.Valid {
			collectionMetadata.FloatValue = &floatValue.Float64
		} else {
			collectionMetadata.FloatValue = nil
		}

		metadata = append(metadata, collectionMetadata)
		currentCollection.CollectionMetadata = metadata
	}
	log.Info("collections", zap.Any("collections", collections))
	return collections, nil
}

func (s *collectionDb) DeleteCollectionByID(collectionID string) error {
	return s.db.Where("id = ?", collectionID).Delete(&dbmodel.Collection{}).Error
}

func (s *collectionDb) Insert(in *dbmodel.Collection) error {
	err := s.db.Create(&in).Error

	if err != nil {
		// TODO: This only works for MySQL, figure out a way for Postgres.
		log.Error("insert collection failed", zap.String("collectionID", in.ID), zap.Int64("ts", in.Ts), zap.Error(err))
		mysqlErr := err.(*mysql.MySQLError)
		switch mysqlErr.Number {
		case 1062:
			return common.ErrCollectionUniqueConstraintViolation
		}
		return err
	}
	return nil
}

func generateCollectionUpdatesWithoutID(in *dbmodel.Collection) map[string]interface{} {
	ret := map[string]interface{}{}
	if in.Name != nil {
		ret["name"] = *in.Name
	}
	if in.Topic != nil {
		ret["topic"] = *in.Topic
	}
	if in.Dimension != nil {
		ret["dimension"] = *in.Dimension
	}
	return ret
}

func (s *collectionDb) Update(in *dbmodel.Collection) error {
	updates := generateCollectionUpdatesWithoutID(in)
	return s.db.Model(&dbmodel.Collection{}).Where("id = ?", in.ID).Updates(updates).Error
}
