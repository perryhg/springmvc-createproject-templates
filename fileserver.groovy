@Grapes([
@Grab('org.eclipse.jetty.aggregate:jetty-server:8.1.2.v20120308'),
@Grab('org.eclipse.jetty.aggregate:jetty-servlet:8.1.2.v20120308'),
@Grab('javax.servlet:javax.servlet-api:3.0.1')
])
@GrabConfig(systemClassLoader=true)

import org.eclipse.jetty.server.*
import org.eclipse.jetty.servlet.*
import org.eclipse.jetty.server.handler.*
import groovy.transform.Field


	@Field Server server

	public void startServer()
	{
		startServerNoJoin()
		server.join();
	}

	public void startServerNoJoin()
	{
		server = new Server(8090);
		ResourceHandler resourceHandler = new ResourceHandler();
		resourceHandler.setDirectoriesListed(true);
		resourceHandler.setResourceBase(".");
		resourceHandler.setStylesheet("");

			HandlerList handlers = new HandlerList();
		//handlers.setHandlers(new Handler[] { resourceHandler, new DefaultHandler() });
		handlers.addHandler(resourceHandler);
		handlers.addHandler(new DefaultHandler());

		// NCSARequestLog requestLog = new NCSARequestLog(null);
		// RequestLogHandler requestLogHandler = new RequestLogHandler();
		// requestLogHandler.setRequestLog(requestLog);
		// handlers.addHandler(requestLogHandler);

		server.setHandler(handlers);

		server.start();
		
	}

	public void stopServer()
	{
		server.stop()
	}

	startServer()