// Code generated by mockery v2.42.1. DO NOT EDIT.

package mocks

import mock "github.com/stretchr/testify/mock"

// isUpdateSegmentRequest_MetadataUpdate is an autogenerated mock type for the isUpdateSegmentRequest_MetadataUpdate type
type isUpdateSegmentRequest_MetadataUpdate struct {
	mock.Mock
}

// isUpdateSegmentRequest_MetadataUpdate provides a mock function with given fields:
func (_m *isUpdateSegmentRequest_MetadataUpdate) isUpdateSegmentRequest_MetadataUpdate() {
	_m.Called()
}

// newIsUpdateSegmentRequest_MetadataUpdate creates a new instance of isUpdateSegmentRequest_MetadataUpdate. It also registers a testing interface on the mock and a cleanup function to assert the mocks expectations.
// The first argument is typically a *testing.T value.
func newIsUpdateSegmentRequest_MetadataUpdate(t interface {
	mock.TestingT
	Cleanup(func())
}) *isUpdateSegmentRequest_MetadataUpdate {
	mock := &isUpdateSegmentRequest_MetadataUpdate{}
	mock.Mock.Test(t)

	t.Cleanup(func() { mock.AssertExpectations(t) })

	return mock
}
