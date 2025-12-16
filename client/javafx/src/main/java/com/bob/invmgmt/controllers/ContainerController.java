/*
 * simple controller for all container operations to the backend.
 */
package com.bob.invmgmt.controllers;

import com.bob.invmgmt.Dao;
import com.bob.invmgmt.models.Container;
import com.bob.invmgmt.models.LocateContainer;

public class ContainerController {
	Dao dao = new Dao();
	
	public Container getContainerByBarcode(String barcode) throws Exception {
		return dao.getContainerByBarcode(barcode);
	}
	
	public Container getContainer(Integer id) throws Exception {
		return dao.getContainer(id);
	}	
	
	public Container addContainer(Container cntr) throws Exception {
		return dao.addContainer(cntr);
	}
	
	public Container updateContainer(Container cntr) throws Exception {
		return dao.updateContainer(cntr);
	}
	
	public Container deleteContainer(Container cntr) throws Exception {
		return dao.deleteContainer(cntr);
	}
	
	public Container locateContainer(LocateContainer locateData) throws Exception {
		return dao.locateContainer(locateData);
	}
}
