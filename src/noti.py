## notification template
import os
def mail_me(mail_path='/usr/bin/mail', 

            subj='Parallel Job Finished',
            contents='Job Finished',
            addr ='youngung.jeong@gmail.com'):
    iflag = os.system("echo '%s' | %s -s '%s' %s"%(
        contents, mail_path, subj, addr))
    if iflag!=0: print 'Error in sending the notification'
    
