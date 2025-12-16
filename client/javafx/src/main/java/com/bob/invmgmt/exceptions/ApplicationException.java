/*
 * a class defining a specific application exception, usually used to contain validation error messages
 * or any error messages specified by the application itself.  it has the ability to contain
 * several messages for when a bunch of fields on a form (ie, pick list search) fail validation.
 * 
 * primary use (besides multiple messages) is to separate these errors from anything else which 
 * might occur. 
 */
package com.bob.invmgmt.exceptions;

import java.util.List;
import java.util.Arrays;

public class ApplicationException extends Exception {
	private static final long serialVersionUID = 1L;
	private List<String> messages;
	
	public ApplicationException(String [] messages) {
		this.messages = Arrays.asList(messages);
	}
	
	public ApplicationException(List<String> messages) {
		this.messages = messages;
	}
	
	public ApplicationException(String message) {
		this(new String [] {message});
	}
	
	public List<String> getMessages() {
		return this.messages;
	}
	
	@Override
	public String getMessage() {
		return String.join("\n",  this.messages);
	}
}
