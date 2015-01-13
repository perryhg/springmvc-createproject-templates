import groovy.swing.SwingBuilder
import java.awt.BorderLayout as BL
import javax.swing.*
import java.awt.*
import java.awt.event.ItemEvent
import templateutil
import fileserver

count = 0
tmplutil = new templateutil()
fs = new fileserver()

def buildGUI(){
	new SwingBuilder().edt {
		frame(title:'Spring Template Builder', size:[700,150], show: true, defaultCloseOperation:JFrame.EXIT_ON_CLOSE) {
			borderLayout(constraints:BL.SOUTH)
			panel(constraints: BL.NORTH)
			{
				borderLayout()
				textlabel = label(text:"Click the button!", constraints: BL.NORTH)
				panel(constraints:BL.SOUTH)
				{
					tlversion = label(text:"version:")
					textField = textField(constraints: BL.SOUTH)
					textField.setPreferredSize( new Dimension( 200, 24 ) )
				}
			}
			panel(constraints: BL.CENTER){
				button(text:'Extract',
					actionPerformed: {
						//count++;
						//textlabel.text = "Clicked ${count} time(s).";
						tmplutil.extractEntries()
						tmplutil.extractTemplate()
						textField.setText(tmplutil.readVersionTmpl())
						textlabel.text = "Extracted"
						//println "clicked"
						})
				button(text:'Read Version',
					actionPerformed: {
						textField.setText(tmplutil.readVersionTmpl())
						textlabel.text = "Version read"
						})
				button(text:'Update Version',

					actionPerformed: {
						tmplutil.updateVersion(textField.getText())
						textlabel.text = "Version updated"
						//count++;
						//textlabel.text = "Clicked ${count} time(s).";
						//println "clicked"
						})
				button(text:'Repack',
					actionPerformed: {
						tmplutil.repackTmpl()
						tmplutil.repackTmplWithDesc()
						tmplutil.updateSize()
						textlabel.text = "Repacked!"
						println "Repacked!"
						//count++;
						//textlabel.text = "Clicked ${count} time(s).";
						//println "clicked"
						})
				toggleButton(text:'Local Server', itemStateChanged:{ev->
					//println ev.getClass().getName()
					if(ev.getStateChange()==ItemEvent.SELECTED)
					{
						println 'selected'
						fs.startServerNoJoin()
						textlabel.text = "local http server started"
					}
					else
					{
						println 'deselected'
						fs.stopServer()
						textlabel.text = "local http server stopped"
					}
					})
			}
		}
	}
}

buildGUI()
