#############################################################
#
# mc
#
#############################################################

MC_VERSION = 4.8.1.6

MC_SOURCE = mc-$(MC_VERSION).tar.bz2
MC_SITE = http://www.midnight-commander.org/downloads
MC_AUTORECONF = NO 
MC_INSTALL_STAGING = NO
MC_INSTALL_TARGET = YES
MC_LIBTOOL_PATCH = NO

MC_DEPENDENCIES = libglib2

MC_CONF_ENV = fu_cv_sys_stat_statfs2_bsize=yes
MC_CONF_OPT = --disable-doxygen-doc --with-screen=ncurses \
	--with-ncurses-includes=$(STAGING)/usr \
	--with-ncurses-libs=$(STAGING)/usr

$(eval $(call AUTOTARGETS,package,mc))