# -*- coding: utf-8 -*-
##############################################################################
#
#    Smart Solution bvba
#    Copyright (C) 2010-Today Smart Solution BVBA (<http://www.smartsolution.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
############################################################################## 

from osv import osv, fields
from openerp.tools.translate import _
import time
import csv
import base64


class account_proacc_api(osv.osv_memory):

    _name = "account.proacc.api"

    _columns = {
        'file_name': fields.char('File Name', size=128, readonly=True),
        'file': fields.binary('Save File', readonly=True),
    }
        

    def customer_export(self, cr, uid, ids, context=None):
        obj = self.pool.get('res.partner')
        customer_ids = obj.search(cr, uid, [('customer','=',True),('supplier','=',False),('proacc_exported','=',False),("is_company","=",True)])
        if not customer_ids:
            return False

        customers = obj.browse(cr, uid, customer_ids)
        filename = '/tmp/partners_' + time.strftime("%Y%m%d") + ".txt"

        with open(filename, 'wb') as proaccfile:
        
            write = csv.writer(proaccfile, delimiter="\t")

            for customer in customers:

		inv_ids = self.pool.get('account.invoice').search(cr, uid, [('partner_id','=',customer.id),('state','=','open')])
		if not inv_ids:
		    continue

                customer_code = str(customer.ref)
                vat = ""
                company_nbr = ""
                if customer.vat:
                    vat = customer.vat
                    #vat[2] == ' ':
                    company_nbr = customer.vat[3:]
                if customer.lang:
                    if customer.lang[0:2] == 'en':
                        lang = "E"
                    elif customer.lang[0:2] == 'nl':
                        lang = "N"
                    elif customer.lang[0:2] == 'fr':
                        lang = "F"
                    elif customer.lang[0:2] == 'de':
                        lang = "D"
                    else:
                        lang = ""
                bank_account = ""
                if customer.bank_ids:
                    bank = customer.bank_ids[0]
                    if bank.state == 'iban':
                        bank_account = bank.acc_number[5:].replace(" ","")
                        bank_account_iban = bank.acc_number[5:].replace(" ",".")
                if customer.vat_subjected:
                    vat_subjected = 1
                else:
                    vat_subjected = 2

                customer_name  = customer.name.encode('utf-8')
                city  = customer.city and customer.city.encode('utf-8') or ""
                street  = customer.street and customer.street.encode('utf-8') or ""
                street2  = customer.street2 and customer.street2.encode('utf-8') or ""
		if customer.country_id.code == 'BE':
		    country_code = ""
		    country_name = ""
		else:
		    country_code = customer.country_id and customer.country_id.code or ""
		    country_name = customer.country_id and customer.country_id.name or ""

                row = [1,
                    customer_code,"","",
                    customer_name,"","",
                    street or "",
                    customer.zip or "",
                    city or "",
                    country_code,
                    country_name,
                    customer.phone or "",
                    customer.fax or "",
                    customer.email or "",
                    vat,
                    lang,
                    customer.property_payment_term.proacc_code or "",
                    bank_account,
                    customer.country_id.currency_id.name,
                    "","","","","","","","","","",
                    customer.property_account_receivable.code or "","",
                    vat_subjected,
                    customer.credit_limit or "",
                    "","","","","","","","","","","","",
                    customer.mobile or "",
                    street2 or "",
                    "","","","","","last"
                    
                ]
                    
                print "ROW:",row
                
                write.writerow(row)
                obj.write(cr, uid, [customer.id], {'proacc_exported':True})

        with open(filename, 'rU') as csvfile:
            file_data = csvfile.read()

        model_data_ids =  self.pool.get('ir.model.data').search(cr, uid,[('model','=','ir.ui.view'),('name','=','view_proacc_file_save')], context=context)
        resource_id =  self.pool.get('ir.model.data').read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
        filedata = base64.encodestring(file_data)

        self.write(cr, uid, ids[0], {'file':filedata, 'file_name':filename[5:]})

        return {
            'name': _('Save Customers ProAcc File'),
            'context': context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.proacc.api',
            'views': [(resource_id,'form')],
            'view_id': 'view_proacc_file_save',
            'res_id': ids[0],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

        return True


    def supplier_export(self, cr, uid, ids, context=None):
        obj = self.pool.get('res.partner')
        suuplier_ids = obj.search(cr, uid, [('customer','=',False),('supplier','=',True),('proacc_exported','=',False)])

        return True


    def invoice_export(self, cr, uid, ids, context=None):
        obj = self.pool.get('account.invoice')
        invoice_ids = obj.search(cr, uid, [('type','=','out_invoice'),('state','=','open'),('proacc_exported','=',False)])
        if not invoice_ids:
            return False

        filename = '/tmp/invoices_' + time.strftime("%Y%m%d") + ".txt"
        invoices = obj.browse(cr, uid, invoice_ids)
   
        with open(filename, 'wb') as csvfile:
        
            write = csv.writer(csvfile, delimiter="\t")

            for invoice in invoices:

                doc_type = "F"
                doc_code = "FAKT"
                doc_number = invoice.number
                if not invoice.partner_id.ref:
                    raise osv.except_osv(_('Error'), _('No reference code could be found for the customer:%s'%(invoice.partner_id.name)))
                client_code = invoice.partner_id.ref
                doc_date = time.strftime("%d/%m/%Y", time.strptime(invoice.date_invoice, "%Y-%m-%d"))
                our_ref = "FAKT " + invoice.number
                your_ref = invoice.name or ""
                currency = invoice.currency_id.name
                currency_rate = invoice.currency_id.rate or ""
                if invoice.partner_id.vat_subjected:
                    vat_status = 1
                else:
                    vat_status = 2
                representative = ""
                payment_method = invoice.payment_term and invoice.payment_term.proacc_code or ""
                due_date = invoice.date_due and time.strftime("%d/%m/%Y", time.strptime(invoice.date_due, "%Y-%m-%d"))
                overall_discount = ""
                fin_discount = ""
                credit_limit = ""

                first_line = True   

                for line in invoice.invoice_line:
                    if first_line:
                        proacc_code = 1
                        first_line = False
                    else:
                        proacc_code = 3
                    product = line.product_id and line.product_id.default_code or ""
                    description = line.product_id and line.product_id.name.encode('utf8') or ""
                    number = str(line.quantity).replace('.',',')
                    unit_price = str(line.price_unit).replace('.',',')
                    vat_percent = line.invoice_line_tax_id and str(line.invoice_line_tax_id[0].amount * 100).replace('.',',') or "0,0" # Should be improved for multiple and complex taxes
                    line_discount = ""
                    fin_account = line.account_id.code
                    ana_account = "" # Not used at neopaul or else: line.account_analytic_id.code
                    quantity = ""

                    row = [
                        proacc_code,
                        doc_type,
                        doc_code,
                        doc_number,
                        client_code,
                        doc_date,
                        our_ref,
                        your_ref,
                        currency,
                        currency_rate,
                        vat_status,
                        representative,
                        payment_method,
                        due_date,
                        overall_discount,
                        fin_discount,
                        credit_limit,
                        product,
                        description,
                        number,
                        unit_price,
                        vat_percent,
                        line_discount,
                        fin_account,
                        ana_account,
                        quantity
                    ]
                    #print "ROW:",row
                    write.writerow(row)

                #obj.write(cr, uid, [invoice.id], {'proacc_exported':True})

            proacc_code = 99

            last_row = [
                proacc_code,"","","",client_code
            ]
            write.writerow(last_row)


        with open(filename, 'rU') as csvfile:
            file_data = csvfile.read()

        model_data_ids =  self.pool.get('ir.model.data').search(cr, uid,[('model','=','ir.ui.view'),('name','=','view_proacc_file_save')], context=context)
        resource_id =  self.pool.get('ir.model.data').read(cr, uid, model_data_ids, fields=['res_id'], context=context)[0]['res_id']
        filedata = base64.encodestring(file_data)

        self.write(cr, uid, ids[0], {'file':filedata, 'file_name':filename[5:]})

        return {
            'name': _('Save Invoice ProAcc File'),
            'context': context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.proacc.api',
            'views': [(resource_id,'form')],
            'view_id': 'view_proacc_file_save',
            'res_id': ids[0],
            'type': 'ir.actions.act_window',
            'target': 'new',
        }

        return True



class account_proacc_payment_import_wizard(osv.osv_memory):

    _name = 'account.proacc.payment.import.wizard'

    _columns = {
        'proacc_file': fields.binary('ProAcc File', required=True),
        'proacc_filename': fields.char('ProAcc Filename', size=128, required=True),
    }

    def _validate_payment(self, cr, uid, invoice, amount, pay_date, account, context=None):
        """Create and validate the payment"""
        
        #Find the bank journal
        jrn_obj = self.pool.get('account.journal')
        jrn_ids = jrn_obj.search(cr, uid, [('code','=','BNK')])
        jrn = jrn_obj.browse(cr, uid, jrn_ids[0])

        voucher_vals = { 
            'type': 'receipt',
            'name': invoice.number,
            'partner_id': invoice.partner_id.id,
            'journal_id': jrn.id,
            'account_id': account or jrn.default_credit_account_id.id,
            'company_id': invoice.company_id.id,
            'currency_id': invoice.company_id.currency_id.id,
            'date': pay_date,
            'amount': amount,
            'line_amount': amount, 
            'period_id': invoice.period_id.id,
        }
        voucher_vals.update(self.pool.get('account.voucher').onchange_partner_id(cr, uid, [], 
            partner_id = invoice.partner_id.id,
            journal_id = jrn.id,
            amount = amount,
            currency_id = invoice.company_id.currency_id.id,
            ttype = 'receipt',
            date = pay_date,
            context = context
        )['value'])
        line_drs = []
        for line_dr in voucher_vals['line_dr_ids']:
            line_drs.append((0, 0, line_dr))
        voucher_vals['line_dr_ids'] = line_drs
        line_crs = []
        for line_cr in voucher_vals['line_cr_ids']:
            line_crs.append((0, 0, line_cr))
        voucher_vals['line_cr_ids'] = line_crs
        voucher_id = self.pool.get('account.voucher').create(cr, uid, voucher_vals, context=context)
        vouchers = self.pool.get('account.voucher').action_move_line_create(cr, uid, [voucher_id], context=context)

        return vouchers

    def payment_import(self, cr, uid, ids, context=None):
        """Import payments, create vouchers and validate them"""
        voucher = self.pool.get('account.voucher')
        print "context:",context

        wizard = self.browse(cr, uid, ids)[0]

        tmpfilename = '/tmp/test.csv'
        tmpfile = open(tmpfilename, 'w+')
        tmpfile.write(base64.decodestring(wizard.proacc_file))
        tmpfile.close()
        tmpfile = open(tmpfilename, 'rU')
        reader = csv.reader(tmpfile, delimiter="\t")

        for row in reader:
            print row
            invoice = self.pool.get('account.invoice').search(cr, uid, [('number','=',row[0])])
            if invoice and len(invoice) == 1:
                inv = self.pool.get('account.invoice').browse(cr, uid, invoice)[0]
                print "Invoice found",inv.number
                account_id = self.pool.get('account.account').search(cr, uid, [('code','=',row[4])])
                amount = float(row[1].replace(',','.'))
                pay_date = time.strftime("%Y-%m-%d", time.strptime(row[3], "%d/%m/%Y"))

                payres = self._validate_payment(cr, uid, inv, amount, pay_date, account_id, context=None)

        tmpfile.close()

        return True


class res_partner(osv.osv):

    _inherit = "res.partner"

    def write(self, cr, uid ,ids, vals, context=None):
        """Reset the proacc exported flag if the partner is modified"""
        if 'proacc_exported' not in vals:
                vals['proacc_exported'] = False
        res = super(res_partner, self).write(cr, uid, ids, vals=vals, context=context)
        return res

    _columns = {
        "proacc_exported": fields.boolean('ProAcc Exported'),
    }

class account_invoice(osv.osv):

    _inherit = "account.invoice"

#    def write(self, cr, uid ,ids, vals, context=None):
#        """Reset the proacc exported flag if the invoice is modified"""
#        if 'proacc_exported' not in vals:
#                vals['proacc_exported'] = False
#        res = super(account_invoice, self).write(cr, uid, ids, vals, context=context)
#        return res

    _columns = {
        "proacc_exported": fields.boolean('ProAcc Exported'),
    }

class account_payment_term(osv.osv):

    _inherit = "account.payment.term"

    _columns = {
        "proacc_code": fields.char("ProAcc Code", size=3),
    }

class account_fiscal_position(osv.osv):

    _inherit = "account.fiscal.position"

    _columns = {
        "proacc_code": fields.char("ProAcc Code", size=3),
    }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
