/*
 * exception indicating that something (usually a container) was not found, ie. invalid. 
 */
package com.bob.invmgmt.exceptions;

public class NotFoundException extends Exception {
		private static final long serialVersionUID = 1L;

		public NotFoundException() {
			super("Record not found");
		}
		
		public NotFoundException(String message) {
			super(message);
		} 
}
