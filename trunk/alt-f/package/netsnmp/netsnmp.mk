#############################################################
#
# netsnmp
#
#############################################################
#NETSNMP_VERSION:=5.4.2.1
#NETSNMP_VERSION:=5.4.3
NETSNMP_VERSION:=5.5.1
NETSNMP_SITE:=http://$(BR2_SOURCEFORGE_MIRROR).dl.sourceforge.net/sourceforge/net-snmp/
NETSNMP_DIR:=$(BUILD_DIR)/net-snmp-$(NETSNMP_VERSION)
NETSNMP_SOURCE:=net-snmp-$(NETSNMP_VERSION).tar.gz
NETSNMP_INSTALL_STAGING = YES
NETSNMP_LIBTOOL_PATCH = NO
NETSNMP_INSTALL_TARGET_OPT = DESTDIR=$(TARGET_DIR) installprogs installlibs installsubdirs
NETSNMP_INSTALL_STAGING_OPT = DESTDIR=$(STAGING_DIR) installprogs installlibs installheaders

NETSNMP_WO_TRANSPORT:=
ifneq ($(BR2_INET_IPX),y)
NETSNMP_WO_TRANSPORT+= IPX
endif
ifneq ($(BR2_INET_IPV6),y)
NETSNMP_WO_TRANSPORT+= UDPIPv6 TCPIPv6
endif

ifeq ($(BR2_ENDIAN),"BIG")
NETSNMP_ENDIAN=big
else
NETSNMP_ENDIAN=little
endif

ifeq ($(BR2_PACKAGE_OPENSSL),y)
NETSNMP_CONFIGURE_OPENSSL:=--with-openssl=$(STAGING_DIR)/usr
else
NETSNMP_CONFIGURE_OPENSSL:=--without-openssl
endif

NETSNMP_CONF_OPT = $(NETSNMP_CONFIGURE_OPENSSL) \
	--with-out-transports="$(NETSNMP_WO_TRANSPORT)" --enable-mini-agent \
	--disable-embedded-perl --disable-perl-cc-checks --without-perl-modules \
	--without-kmem-usage --without-rsaref --disable-debugging --with-defaults \
	--with-sys-location="Unknown" --with-sys-contact="root" \
	--with-endianness=$(NETSNMP_ENDIAN) \
	--with-persistent-directory=/var/lib/snmp \
	--enable-ucd-snmp-compatibility \
	--enable-shared --disable-static \
	--without-rpm --disable-manuals 

NETSNMP_CONF_ENV = ac_cv_NETSNMP_CAN_USE_SYSCTL=yes 

$(eval $(call AUTOTARGETS,package,netsnmp))

$(NETSNMP_HOOK_POST_INSTALL):
	rm -rf $(TARGET_DIR)/usr/share/man $(TARGET_DIR)/usr/share/doc $(TARGET_DIR)/usr/share/info
	# Copy the .conf files.
	$(INSTALL) -D -m 0644 $(NETSNMP_DIR)/EXAMPLE.conf $(TARGET_DIR)/etc/snmp/snmpd.conf
	-mv $(TARGET_DIR)/usr/share/snmp/mib2c*.conf $(TARGET_DIR)/etc/snmp
	# Install the "broken" headers
	$(INSTALL) -D -m 0644 $(NETSNMP_DIR)/agent/mibgroup/struct.h $(STAGING_DIR)/usr/include/net-snmp/agent/struct.h
	$(INSTALL) -D -m 0644 $(NETSNMP_DIR)/agent/mibgroup/util_funcs.h $(STAGING_DIR)/usr/include/net-snmp/util_funcs.h
	$(INSTALL) -D -m 0644 $(NETSNMP_DIR)/agent/mibgroup/mibincl.h $(STAGING_DIR)/usr/include/net-snmp/library/mibincl.h
	$(INSTALL) -D -m 0644 $(NETSNMP_DIR)/agent/mibgroup/header_complex.h $(STAGING_DIR)/usr/include/net-snmp/agent/header_complex.h
	touch $@
