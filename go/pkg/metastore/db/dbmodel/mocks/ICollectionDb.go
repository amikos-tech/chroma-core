// Code generated by mockery v2.42.0. DO NOT EDIT.

package mocks

import (
	dbmodel "github.com/chroma-core/chroma/go/pkg/metastore/db/dbmodel"
	mock "github.com/stretchr/testify/mock"
)

// ICollectionDb is an autogenerated mock type for the ICollectionDb type
type ICollectionDb struct {
	mock.Mock
}

// DeleteAll provides a mock function with given fields:
func (_m *ICollectionDb) DeleteAll() error {
	ret := _m.Called()

	if len(ret) == 0 {
		panic("no return value specified for DeleteAll")
	}

	var r0 error
	if rf, ok := ret.Get(0).(func() error); ok {
		r0 = rf()
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// DeleteCollectionByID provides a mock function with given fields: collectionID
func (_m *ICollectionDb) DeleteCollectionByID(collectionID string) (int, error) {
	ret := _m.Called(collectionID)

	if len(ret) == 0 {
		panic("no return value specified for DeleteCollectionByID")
	}

	var r0 int
	var r1 error
	if rf, ok := ret.Get(0).(func(string) (int, error)); ok {
		return rf(collectionID)
	}
	if rf, ok := ret.Get(0).(func(string) int); ok {
		r0 = rf(collectionID)
	} else {
		r0 = ret.Get(0).(int)
	}

	if rf, ok := ret.Get(1).(func(string) error); ok {
		r1 = rf(collectionID)
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}

// GetCollections provides a mock function with given fields: collectionID, collectionName, tenantID, databaseName
func (_m *ICollectionDb) GetCollections(collectionID *string, collectionName *string, tenantID string, databaseName string) ([]*dbmodel.CollectionAndMetadata, error) {
	ret := _m.Called(collectionID, collectionName, tenantID, databaseName)

	if len(ret) == 0 {
		panic("no return value specified for GetCollections")
	}

	var r0 []*dbmodel.CollectionAndMetadata
	var r1 error
	if rf, ok := ret.Get(0).(func(*string, *string, string, string) ([]*dbmodel.CollectionAndMetadata, error)); ok {
		return rf(collectionID, collectionName, tenantID, databaseName)
	}
	if rf, ok := ret.Get(0).(func(*string, *string, string, string) []*dbmodel.CollectionAndMetadata); ok {
		r0 = rf(collectionID, collectionName, tenantID, databaseName)
	} else {
		if ret.Get(0) != nil {
			r0 = ret.Get(0).([]*dbmodel.CollectionAndMetadata)
		}
	}

	if rf, ok := ret.Get(1).(func(*string, *string, string, string) error); ok {
		r1 = rf(collectionID, collectionName, tenantID, databaseName)
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}

// Insert provides a mock function with given fields: in
func (_m *ICollectionDb) Insert(in *dbmodel.Collection) error {
	ret := _m.Called(in)

	if len(ret) == 0 {
		panic("no return value specified for Insert")
	}

	var r0 error
	if rf, ok := ret.Get(0).(func(*dbmodel.Collection) error); ok {
		r0 = rf(in)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// Update provides a mock function with given fields: in
func (_m *ICollectionDb) Update(in *dbmodel.Collection) error {
	ret := _m.Called(in)

	if len(ret) == 0 {
		panic("no return value specified for Update")
	}

	var r0 error
	if rf, ok := ret.Get(0).(func(*dbmodel.Collection) error); ok {
		r0 = rf(in)
	} else {
		r0 = ret.Error(0)
	}

	return r0
}

// UpdateLogPositionAndVersion provides a mock function with given fields: collectionID, logPosition, currentCollectionVersion
func (_m *ICollectionDb) UpdateLogPositionAndVersion(collectionID string, logPosition int64, currentCollectionVersion int32) (int32, error) {
	ret := _m.Called(collectionID, logPosition, currentCollectionVersion)

	if len(ret) == 0 {
		panic("no return value specified for UpdateLogPositionAndVersion")
	}

	var r0 int32
	var r1 error
	if rf, ok := ret.Get(0).(func(string, int64, int32) (int32, error)); ok {
		return rf(collectionID, logPosition, currentCollectionVersion)
	}
	if rf, ok := ret.Get(0).(func(string, int64, int32) int32); ok {
		r0 = rf(collectionID, logPosition, currentCollectionVersion)
	} else {
		r0 = ret.Get(0).(int32)
	}

	if rf, ok := ret.Get(1).(func(string, int64, int32) error); ok {
		r1 = rf(collectionID, logPosition, currentCollectionVersion)
	} else {
		r1 = ret.Error(1)
	}

	return r0, r1
}

// NewICollectionDb creates a new instance of ICollectionDb. It also registers a testing interface on the mock and a cleanup function to assert the mocks expectations.
// The first argument is typically a *testing.T value.
func NewICollectionDb(t interface {
	mock.TestingT
	Cleanup(func())
}) *ICollectionDb {
	mock := &ICollectionDb{}
	mock.Mock.Test(t)

	t.Cleanup(func() { mock.AssertExpectations(t) })

	return mock
}
