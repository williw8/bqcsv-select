# Expression should be of the form:
# <select mnemonic> <column expression> [<where mnemonic> <where expression>]
# <select mnemonic> is either "SELECT" or "select"
# <where mnemonic> is either "WHERE" or "where"
# <column expression> is either "*" or a comma-separated list of column names
# <where expression> is of the form <column name> <operator> <column value>
# <column name> is a column name
# <operator> is one of "=","<",">","<=", or ">="
# <column value> is a comparison value

import wx
from csvdb import csvmemory
from csvdb import csvfile
from csvdb import csvdb
from actions import utils

H_SPACER = 5
V_SPACER = 5

class SelectDialog(wx.Dialog):

  def __init__(self,parent,table):
    wx.Dialog.__init__(self,parent)
    self.table = table
    self.expression = None

    self.initUI()
    self.SetSize((320,240))
    self.SetTitle("Select")


  def setPath(self,v):
    '''
    Required
    '''
    self.path = v

  def initUI(self):
    vbox = wx.BoxSizer(wx.VERTICAL)

    vbox.AddSpacer(V_SPACER)

    hbox = wx.BoxSizer(wx.HORIZONTAL)
    hbox.AddSpacer(H_SPACER)
    self.expression_ctrl = wx.TextCtrl(self,size=(300,-1))
    self.expression_ctrl.SetEditable(True)
    hbox.Add(self.expression_ctrl)
    vbox.Add(hbox);

    vbox.AddSpacer(V_SPACER)

    hbox = wx.BoxSizer(wx.HORIZONTAL)
    self.ok_button = wx.Button(self,wx.ID_OK)
    hbox.AddSpacer(H_SPACER)
    hbox.Add(self.ok_button)
    hbox.AddSpacer(H_SPACER)
    self.cancel_button = wx.Button(self,wx.ID_CANCEL)
    hbox.AddSpacer(H_SPACER)
    hbox.Add(self.cancel_button)
    hbox.AddSpacer(H_SPACER)
    vbox.Add(hbox)

    self.ok_button.Bind(wx.EVT_BUTTON,self.onOK)
    self.cancel_button.Bind(wx.EVT_BUTTON,self.onCancel)

    self.SetSizer(vbox)

  def onOK(self,event):
    self.expression = self.expression_ctrl.GetValue()
    self.EndModal(wx.ID_OK)

  def onCancel(self,event):
    self.EndModal(wx.ID_CANCEL)

  def getExpression(self):
    return self.expression

def doSelect(table,expression,memdb):
  table.reset()

  se = csvdb.SelectExpression(expression,table)
  if False == se.isValid():
    wx.MessageBox("Invalid select expression: " + se.getText(),'Info',wx.OK|wx.ICON_INFORMATION)
    return memdb
  new_rows = table.selectWithSelectExpression(se)
  new_header = list() 
  for col in se.getSelectColumns():
    new_header.append(col)
  memdb.setHeader(new_header)
  for row in new_rows:
    memdb.appendRow(row) 
  return memdb

class SelectPlugin(object):

  def __init__(self,parent_frame):
    self.path = None
    self.parent_frame = parent_frame
 
  def getLabel(self):
    '''
    Required
    '''
    return 'Select'

  def getDescription(self):
    '''
    Required
    '''
    return 'Select columns from open file'

  def setPath(self,v):
    self.path = v

  def doAction(self,table):
    '''
    Required
    '''
    if None is table:
      wx.MessageBox('Missing table', 'Info', wx.OK | wx.ICON_INFORMATION)
      return
    dialog = SelectDialog(self.parent_frame,table)
    dialog.SetSize((400,-1))
    chk = dialog.ShowModal()
    if wx.ID_OK == chk:
      expression = dialog.getExpression()
      memdb = csvmemory.MemoryWriter()
      new_header = []
      for col in table.getHeader():
        new_header.append(col)
      idx = 0
      memdb.setHeader(new_header) 
          
      doSelect(table,expression,memdb)
            
      path = utils.getTempFilename()
      memdb.save(path)
      self.parent_frame.addPage(path,delete_on_exit=True)

def getPlugin(parent_frame):
  return SelectPlugin(parent_frame)


