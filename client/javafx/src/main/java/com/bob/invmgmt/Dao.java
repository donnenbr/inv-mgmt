/*
 * The dao used to access and update data with the backend.
 * it is based on JSON web services.
 */
package com.bob.invmgmt;

import org.apache.hc.client5.http.classic.methods.HttpGet;
import org.apache.hc.client5.http.classic.methods.HttpPost;
import org.apache.hc.client5.http.classic.methods.HttpPut;
import org.apache.hc.client5.http.classic.methods.HttpDelete;
import org.apache.hc.client5.http.impl.classic.CloseableHttpClient;
import org.apache.hc.client5.http.impl.classic.HttpClients;
import org.apache.hc.core5.http.io.entity.EntityUtils;
import org.apache.hc.core5.http.io.entity.StringEntity;

import org.apache.hc.core5.http.HttpStatus;

import java.net.URLEncoder;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.annotation.JsonInclude.Include;
import java.util.Map;
import java.util.List;

import com.bob.invmgmt.models.Container;
import com.bob.invmgmt.models.LocateContainer;
import com.bob.invmgmt.models.PickListItem;
import com.bob.invmgmt.models.PickListResult;
import com.bob.invmgmt.exceptions.*;

public class Dao {
	// getting the base url from system properties is near impossible with mvn and javafx plugin, so we take it from the
	// environment.  no getenv(key, default_value)
	private static final String DEFAULT_BASE_URL = "http://localhost:/service/invmgmt";
	private static final String baseURL;
	private CloseableHttpClient httpclient = null;
	private ObjectMapper mapper;
	static {
		String s = System.getenv("REST_URL");
		if (s == null || s.trim().isEmpty()) {
			baseURL = DEFAULT_BASE_URL;
		}
		else {
			baseURL = s;
		}
	}
	
	public Dao() {
		try {
			httpclient = HttpClients.createDefault();
			// setup the json serializer/deserializer.
			mapper = new ObjectMapper();
			mapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
			mapper.setSerializationInclusion(Include.NON_NULL);
		}
		catch (Throwable t) {
			System.err.println("*** could not instantiate http client - " + t);
			httpclient = null;
		}
	}
	
	// class to get the result of a web service call
	static class Result {
        final int status;
        final String content;

        Result(final int status, final String content) {
            this.status = status;
            this.content = content;
        }
        
        public String toString() {
        	return "Result: status=" + status + ", content=" + content;
        }

    }

	// get the data enclosed in a Result instance and deserialize it into a class
	private Object getData(Result result, Class cls) throws Exception {
		if (result == null) {
			throw new ApplicationException("Result is NULL");
		}
		if (result.status != HttpStatus.SC_OK) {
			if (result.status == HttpStatus.SC_INTERNAL_SERVER_ERROR) {
				if (result.content == null) {
					throw new ApplicationException("Result content is NULL");
				}
				throw new ApplicationException("An application error occurred - " + result.content);
			}
			if (result.status == HttpStatus.SC_NOT_FOUND) {
				throw new NotFoundException();
			}
			else if (result.status != HttpStatus.SC_UNPROCESSABLE_CONTENT) {
				// catch all
				throw new ApplicationException("Unknown application error occurred - status=" + result.status + ", content=" + result.content);
			}
		}
		Map<String, Object> map = (Map<String, Object>)mapper.readValue(result.content, Map.class);
        Boolean success = (Boolean)map.get("success");
        if (success == true) {
        	Map<String,Object> data = (Map<String, Object>)map.get("data");
        	if (data == null) {
        		throw new ApplicationException("No data was returned !!!");
        	}
        	else {
        		// dump the container data
        		Object obj = mapper.convertValue(data, cls);
        		return obj;
        	}
        }
        else {
        	// look for errors
        	List<String> errors = (List<String>)map.get("errors");
        	if (errors == null) {
        		throw new ApplicationException("Call failed but no errors returned");
        	}
        	throw new ApplicationException(errors);
        }
		
	}
	
	// convenience call create a POST request
	private HttpPost makePostRequest(String url, Object data) throws Exception {
		HttpPost request = new HttpPost(url);
		request.addHeader("Accept", "application/json");
		request.addHeader("Content-Type", "application/json");
		String jsonData = mapper.writeValueAsString(data);
		request.setEntity(new StringEntity(jsonData));
		
		return request;
	}
	
	// same for PUT
	private HttpPut makePutRequest(String url, Object data) throws Exception {
		HttpPut request = new HttpPut(url);
		request.addHeader("Accept", "application/json");
		request.addHeader("Content-Type", "application/json");
		String jsonData = mapper.writeValueAsString(data);
		request.setEntity(new StringEntity(jsonData));
		
		return request;
	}
	
	// same for DELETE
	private HttpDelete makeDeleteRequest(String url) throws Exception {
		HttpDelete request = new HttpDelete(url);
		request.addHeader("Accept", "application/json");
		request.addHeader("Content-Type", "application/json");
		
		return request;
	}
	
	// get a container by id
	public Container getContainer(int id) throws Exception {
		String url = baseURL + "/container/" + id;
		HttpGet request = new HttpGet(url);
		final Result result = httpclient.execute(request, response -> {
            return new Result(response.getCode(), EntityUtils.toString(response.getEntity()));
        });
		
        return (Container)getData(result, Container.class);
	}
	
	// get a container by barcode
	public Container getContainerByBarcode(String barcode) throws Exception {
		String url = baseURL + "/container_by_barcode?barcode=" + URLEncoder.encode(barcode, "utf8");
		HttpGet request = new HttpGet(url);
		final Result result = httpclient.execute(request, response -> {
            return new Result(response.getCode(), EntityUtils.toString(response.getEntity()));
        });
		
        return (Container)getData(result, Container.class);
	}
	
	// add a new container
	public Container addContainer(Container cntr) throws Exception {
		String url = baseURL + "/container";
		HttpPost request = makePostRequest(url, cntr);
		final Result result = httpclient.execute(request, response -> {
            return new Result(response.getCode(), EntityUtils.toString(response.getEntity()));
        });
		
        return (Container)getData(result, Container.class);
	}
	
	// update a container
	public Container updateContainer(Container cntr) throws Exception {
		String url = baseURL + "/container/" + cntr.getId();
		HttpPut request = makePutRequest(url, cntr);
		final Result result = httpclient.execute(request, response -> {
            return new Result(response.getCode(), EntityUtils.toString(response.getEntity()));
        });
		
        return (Container)getData(result, Container.class);
	}
	
	// delete a container
	public Container deleteContainer(Container cntr) throws Exception {
		String url = baseURL + "/container/" + cntr.getId();
		HttpDelete request = makeDeleteRequest(url);
		final Result result = httpclient.execute(request, response -> {
            return new Result(response.getCode(), EntityUtils.toString(response.getEntity()));
        });
		
		// it returns the data for the container just deleted.
        return (Container)getData(result, Container.class);
	}
	
	// locate a container
	public Container locateContainer(LocateContainer locateData) throws Exception {
		String url = baseURL + "/locate_container";
		HttpPut request = makePutRequest(url, locateData);
		final Result result = httpclient.execute(request, response -> {
            return new Result(response.getCode(), EntityUtils.toString(response.getEntity()));
        });
		
		// it returns the data for the container just deleted.
        return (Container)getData(result, Container.class);
	}
	
	// perform a pick list request and return the result
	public PickListResult generatePickList(List<PickListItem> requestData) throws Exception {
		String url = baseURL + "/pick_list";
		HttpPost request = makePostRequest(url, requestData);
		long t1 = System.currentTimeMillis();
		final Result result = httpclient.execute(request, response -> {
            return new Result(response.getCode(), EntityUtils.toString(response.getEntity()));
        });
		long t2 = System.currentTimeMillis();
		System.out.println("*** time - " + (t2-t1)/1000.0 + " (sec)");
		return (PickListResult)getData(result, PickListResult.class);
	}
}
